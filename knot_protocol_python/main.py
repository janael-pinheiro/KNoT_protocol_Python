from pika import URLParameters
from pika.exchange_type import ExchangeType
from os import environ
from random import uniform
from datetime import datetime
import yaml
from time import sleep

from knot_protocol_python.infraestructure.adapter.input.connection import AMQPConnection, AMQPChannel, AMQPExchange

from knot_protocol_python.domain.DTO.data_point import DataPointDTO
from knot_protocol_python.infraestructure.adapter.output.DTO.device_schema import DeviceSchema
from knot_protocol_python.domain.entities.device_factory import DeviceFactory
from knot_protocol_python.infraestructure.utils.knot_amqp_options import KNoTExchange


if __name__ == "__main__":
    knot_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDU5Mjc3NzIsImp0aSI6Ijc5N2I4MmJlLWNiMzMtNGFhNi1iYTkwLWZkOTFjNTU3NmEwNCIsImlhdCI6MTY3NDM5MTc3MiwiaXNzIjoiYWpwQGtub3Qub3JnLmJyIiwidHlwZSI6Mn0.TUu_3OJADMblSKXDMUkJu7lzVmUMkzOiNAEfBuXIQVw"
    parameters = URLParameters(environ.get("AMQP_URL"))
    subscriber_connection = AMQPConnection(parameters=parameters).create()
    publisher_connection = AMQPConnection(parameters=parameters).create()
    subscriber_channel = AMQPChannel(connection=subscriber_connection).create()
    BUFFER_LENGTH: int = 1
    subscriber_channel.basic_qos(prefetch_count=BUFFER_LENGTH)
    publisher_channel = AMQPChannel(connection=publisher_connection).create()
    publisher_channel.confirm_delivery()
    AMQPExchange(
        channel=subscriber_channel,
        exchange_name=KNoTExchange.device_exchange.value,
        exchange_type=ExchangeType.direct).declare()
    device = DeviceFactory.create(
        subscriber_channel=subscriber_channel,
        publisher_channel=publisher_channel,
        knot_token=knot_token)
    AMQPExchange(
        channel=subscriber_channel,
        exchange_name=KNoTExchange.data_sent_exchange.value,
        exchange_type=ExchangeType.fanout
    ).declare()
    device.start()
    serialized_device = DeviceSchema().dump(device)
    with open("device.yaml", "w", encoding="utf-8") as file_writer:
        yaml.dump(serialized_device, file_writer)

    print("Publishing data!")
    try:
        while True:
            value = uniform(1.6, 89.2)
            data = DataPointDTO(sensor_id=1, value=f"{value:.2f}", timestamp=str(datetime.utcnow()))
            device.data_points = [data]
            device.publish_data()
            sleep(5)
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        subscriber_channel.close()
        subscriber_connection.close()
        publisher_channel.close()
        publisher_connection.close()
