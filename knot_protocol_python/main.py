from datetime import datetime
from random import uniform
from time import sleep

from knot_protocol_python.domain.DTO.data_point import DataPointDTO
from knot_protocol_python.domain.entities.device_factory import DeviceFactory
from knot_protocol_python.infraestructure.adapter.output.repositories.device_file_repository import \
    DeviceFileRepository

if __name__ == "__main__":
    device_file_repository = DeviceFileRepository(filepath="device.yaml")
    device = DeviceFactory.load_existing_device(device_repository=device_file_repository)
    device.start()
    device_file_repository.save(device=device)

    print("Publishing data!")
    try:
        while True:
            temperature_value = uniform(1.6, 89.2)
            humidity_value = uniform(1.6, 89.2)
            temperature = DataPointDTO(sensor_id=1, value=f"{temperature_value:.2f}", timestamp=str(datetime.utcnow()))
            humidity = DataPointDTO(sensor_id=2, value=f"{humidity_value:.2f}", timestamp=str(datetime.utcnow()))
            device.data = [temperature, humidity]
            device.publish_data()
            sleep(5)
    except Exception as e:
        print(f"Exception: {e}")
