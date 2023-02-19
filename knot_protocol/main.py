from datetime import datetime
from random import uniform
from time import sleep
from sys import argv
from threading import Thread

from knot_protocol.domain.DTO.data_point import DataPointDTO
from knot_protocol import DeviceFileRepository, DeviceFactory
from knot_protocol.domain.DTO.schema import SchemaFactory
from knot_protocol.domain.DTO.event import EventFactory
from knot_protocol.domain.DTO.device_configuration import ConfigurationFactory
from knot_protocol.domain.boundary.output.DTO.knot_amqp_options import KNoTValueType
from knot_protocol.infraestructure.utils.utils import generate_consumer_tag


def publish_data(test_device):
    with test_device:
        print(f"Publishing data for device {test_device.device_id}!")
        try:
            while True:
                temperature_value = uniform(1.6, 89.2)
                humidity_value = uniform(1.6, 89.2)
                temperature = DataPointDTO(sensor_id=1, value=f"{temperature_value:.2f}", timestamp=str(datetime.utcnow()))
                humidity = DataPointDTO(sensor_id=2, value=f"{humidity_value:.2f}", timestamp=str(datetime.utcnow()))
                test_device.data = [temperature, humidity]
                test_device.publish_data()
                sleep(1)
        except Exception as e:
            print(f"Exception: {e}")


def persist_configuration(knot_devices) -> None:
    for knot_device in knot_devices:
        knot_device.unregister()
        device_file_repository = DeviceFileRepository(filepath=f"device_{knot_device.device_id}.yaml")
        device_file_repository.save(device=knot_device)


if __name__ == "__main__":
    number_devices = int(argv[1])
    #device = DeviceFactory.load_existing_device(device_repository=device_file_repository)
    devices = []
    threads = []
    for _ in range(number_devices):
        DEVICE_NAME = generate_consumer_tag()
        temperature_schema = SchemaFactory.create(name="temperature", value_type=KNoTValueType.FLOAT.value, unit=0, type_id=65521)
        temperature_event = EventFactory.create(change=True, time_seconds=5, lower_threshold=1.6, upper_threshold=89.2)
        temperatura_configuration = ConfigurationFactory.create(sensor_id=1, schema=temperature_schema, event=temperature_event)

        humidty_schema = SchemaFactory.create(name="humidity", value_type=KNoTValueType.FLOAT.value, unit=0, type_id=65521)
        humidity_event = EventFactory.create(change=True, time_seconds=5, lower_threshold=1.6, upper_threshold=89.2)
        humidity_configuration = ConfigurationFactory.create(sensor_id=2, schema=humidty_schema, event=humidity_event)

        device = DeviceFactory.create(name=DEVICE_NAME, schema=[temperatura_configuration, humidity_configuration])
        device.start()
        device_thread = Thread(target=publish_data, args=(device,))
        device_thread.start()
        threads.append(device_thread)
        devices.append(device)
    for t in threads:
        t.join()

    persist_configuration(devices)
