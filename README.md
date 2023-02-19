export AMQP_URL=amqp://knot:knot@localhost:5672


# Features
- KNoT State Machine;
- Subscriber message confirmation;
- Publisher message confirmation (need proofs);
- Automatic disconnection recovery;
- Configuration validation;
- Consumer timeout.

# Environment variables
- KNOT_TOKEN;
- CONSUMER_TIMEOUT;
- AMQP_URL.

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


Create new device:
```
temperature_schema = SchemaFactory.create(name="temperature", value_type=KNoTValueType.FLOAT.value, unit=0, type_id=65521)
temperature_event = EventFactory.create(change=True, time_seconds=5, lower_threshold=1.6, upper_threshold=89.2)
temperatura_configuration = ConfigurationFactory.create(sensor_id=1, schema=temperature_schema, event=temperature_event)

humidty_schema = SchemaFactory.create(name="humidity", value_type=KNoTValueType.FLOAT.value, unit=0, type_id=65521)
humidity_event = EventFactory.create(change=True, time_seconds=5, lower_threshold=1.6, upper_threshold=89.2)
humidity_configuration = ConfigurationFactory.create(sensor_id=2, schema=humidty_schema, event=humidity_event)

device = DeviceFactory.create(name="Device 2", schema=[temperatura_configuration, humidity_configuration])
```
## Docker
```sh
$ sudo docker build --file docker/Dockerfile . --no-cache --tag knot_protocol
$ sudo docker run knot_protocol
```