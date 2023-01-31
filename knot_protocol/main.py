from datetime import datetime
from random import uniform
from time import sleep

from knot_protocol.domain.DTO.data_point import DataPointDTO
from knot_protocol import DeviceFileRepository, DeviceFactory


if __name__ == "__main__":
    device_file_repository = DeviceFileRepository(filepath="device.yaml")
    device = DeviceFactory.load_existing_device(device_repository=device_file_repository)
    with device:
        print("Publishing data!")
        counter: int = 0
        limit: int = 10
        try:
            while True:
                temperature_value = uniform(1.6, 89.2)
                humidity_value = uniform(1.6, 89.2)
                temperature = DataPointDTO(sensor_id=1, value=f"{temperature_value:.2f}", timestamp=str(datetime.utcnow()))
                humidity = DataPointDTO(sensor_id=2, value=f"{humidity_value:.2f}", timestamp=str(datetime.utcnow()))
                device.data = [temperature, humidity]
                device.publish_data()
                sleep(1)
                counter += 1
                if counter == limit:
                    break
        except Exception as e:
            print(f"Exception: {e}")

        device_file_repository.save(device=device)
