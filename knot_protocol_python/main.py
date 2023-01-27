from pika import URLParameters
from os import environ
from random import uniform
from datetime import datetime
import yaml
from time import sleep

from knot_protocol_python.infraestructure.adapter.input.connection import AMQPConnection, AMQPChannel

from knot_protocol_python.domain.DTO.data_point import DataPointDTO
from knot_protocol_python.infraestructure.adapter.output.DTO.device_schema import DeviceSchema
from knot_protocol_python.domain.entities.device_factory import DeviceFactory


if __name__ == "__main__":
    knot_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDU5Mjc3NzIsImp0aSI6Ijc5N2I4MmJlLWNiMzMtNGFhNi1iYTkwLWZkOTFjNTU3NmEwNCIsImlhdCI6MTY3NDM5MTc3MiwiaXNzIjoiYWpwQGtub3Qub3JnLmJyIiwidHlwZSI6Mn0.TUu_3OJADMblSKXDMUkJu7lzVmUMkzOiNAEfBuXIQVw"
    parameters = URLParameters(environ.get("AMQP_URL"))
    with AMQPConnection(parameters=parameters) as connection:
        with AMQPChannel(connection=connection) as channel:
            device = DeviceFactory.create(channel=channel, knot_token=knot_token)
            print(type(device.state))
            print(device.token)
            device.start()
            serialized_device = DeviceSchema().dump(device)
            with open("device.yaml", "w", encoding="utf-8") as file_writer:
                yaml.dump(serialized_device, file_writer)

            print("Publishing data!")
            while True:
                value = uniform(1.6, 89.2)
                data = DataPointDTO(sensor_id=1, value=f"{value:.2f}", timestamp=str(datetime.utcnow()))
                device.data_points = [data]
                device.publish_data()
                sleep(5)
