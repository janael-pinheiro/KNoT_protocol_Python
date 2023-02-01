export AMQP_URL=amqp://knot:knot@localhost:5672


# Features
- KNoT State Machine;
- Subscriber message confirmation;
- Publisher message confirmation (need proofs);
- Automatic disconnection recovery;
- Configuration validation.


## Testing
poetry run coverage clean
poetry run coverage run -m pytest -s -v tests
poetry run coverage report
poetry run coverage xml


sudo docker run --rm --network=host -e SONAR_HOST_URL=http://127.0.0.1:9000/ -e SONAR_LOGIN=sqp_3ca62d658b1bab99e7c6d6ca504c91338a6276c1 -v /home/ajp/Documents/Projetos\ pessoais/knot-protocol-python/:/usr/src/ sonarsource/sonar-scanner-cli -Dsonar.projectKey=knot-protocol-sdk-python -Dsonar.sources=. -Dsonar.host.url=http://localhost:9000 -Dsonar.login=sqp_3ca62d658b1bab99e7c6d6ca504c91338a6276c1

## Examples

Imports:

```
from knot_protocol import DeviceFileRepository
device_file_repository = DeviceFileRepository(filepath="device.yaml")
device = DeviceFactory.load_existing_device(device_repository=device_file_repository)
```

Manual start/stop:
```
device.start()
temperature_value = uniform(1.6, 89.2)
humidity_value = uniform(1.6, 89.2)
temperature = DataPointDTO(sensor_id=1, value=f"{temperature_value:.2f}", timestamp=str(datetime.utcnow()))
humidity = DataPointDTO(sensor_id=2, value=f"{humidity_value:.2f}", timestamp=str(datetime.utcnow()))
device.data = [temperature, humidity]
device.publish_data()
device.stop()
```

Using context manager:
```
with device:
    temperature_value = uniform(1.6, 89.2)
    humidity_value = uniform(1.6, 89.2)
    temperature = DataPointDTO(sensor_id=1, value=f"{temperature_value:.2f}", timestamp=str(datetime.utcnow()))
    humidity = DataPointDTO(sensor_id=2, value=f"{humidity_value:.2f}", timestamp=str(datetime.utcnow()))
    device.data = [temperature, humidity]
    device.publish_data()
```

## Docker
```sh
$ sudo docker build --file docker/Dockerfile . --no-cache --tag knot_protocol
$ sudo docker run knot_protocol
```