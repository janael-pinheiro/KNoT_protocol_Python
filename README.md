This project is an unofficial implementation of the [KNoT protocol](https://knot-devel.cesar.org.br/doc/thing/thing.html) in the Python language.

The key features are:
- **KNoT State Machine**: create, register, authenticate, update configuration, publish data and unregister KNoT things;
- **Subscriber message confirmation**: notifies the AMQP broker used by KNoT that messages processed correctly or failed;
- **Automatic disconnection recovery**: automatically re-establishes the connection to the broker automatically in case of failure;
- **Configuration persistence**: persist and load the thing knot configuration from files;
- **Configuration validation**: checks if the device configuration loaded from files is valid according to KNoT;
- **Consumer timeout**: configures the timeout in seconds for receiving messages from the KNoT (default: 5 minutes).

Environment variables:
- KNOT_TOKEN;
- CONSUMER_TIMEOUT;
- AMQP_URL.

Update the values in the scripts/set_venv.sh file and run:
```
source scripts/set_venv.sh
```

## Testing
```
poetry run coverage run -m pytest -s -v tests
poetry run coverage report
poetry run coverage xml
```

## Examples

Imports:

```
from datetime import datetime

from knot_protocol import (
    DeviceFileRepository,
    DeviceFactory,
    DeviceEntity,
    SchemaFactory,
    EventFactory,
    DataPointFactory,
    ConfigurationFactory,
    KNoTValueType,
    DeviceRegistrationRequestSchema,
    DeviceAuthRequestSchema,
    DataPointsSchema,
    UpdateConfigRequestSchema,
    DeviceUnregistrationRequestDTO,
    amqp_data_management_setup,
    logger_factory) 
```

Create a new device:
```
temperature_schema = SchemaFactory.create(name="temperature", value_type=KNoTValueType.FLOAT.value, unit=0, type_id=65521)
temperature_event = EventFactory.create(change=True, time_seconds=5, lower_threshold=1.6, upper_threshold=89.2)
temperatura_configuration = ConfigurationFactory.create(sensor_id=1, schema=temperature_schema, event=temperature_event)

humidty_schema = SchemaFactory.create(name="humidity", value_type=KNoTValueType.FLOAT.value, unit=0, type_id=65521)
humidity_event = EventFactory.create(change=True, time_seconds=5, lower_threshold=1.6, upper_threshold=89.2)
humidity_configuration = ConfigurationFactory.create(sensor_id=2, schema=humidty_schema, event=humidity_event)

logger = logger_factory()
KNOT_TOKEN = environ.get("KNOT_TOKEN")
DEVICE_ID = DeviceEntity.create_id()
(
register_subscriber,
auth_subscriber,
update_config_subscriber,
register_publisher,
auth_publisher,
update_config_publisher,
data_publisher,
unregister_subscriber,
unregister_publisher,
amqp_generator) = amqp_data_management_setup(
    logger=logger,
    knot_token=KNOT_TOKEN,
    device_id=DEVICE_ID)

device = DeviceFactory.create(
    name="Device 2",
    device_id=DEVICE_ID,
    schema=[temperatura_configuration, humidity_configuration],
    amqp_generator=amqp_generator,
    register_subscriber=register_subscriber,
    register_publisher=register_publisher,
    register_serializer=DeviceRegistrationRequestSchema(),
    auth_publisher=auth_publisher,
    auth_subscriber=auth_subscriber,
    device_auth_serializer=DeviceAuthRequestSchema(),
    data_publisher=data_publisher,
    publisher_serializer=DataPointsSchema(),
    unregister_publisher=unregister_publisher,
    unregister_subscriber=unregister_subscriber,
    unregister_serializer=DeviceUnregistrationRequestDTO(),
    update_config_publisher=update_config_publisher,
    update_config_subscriber=update_config_subscriber,
    update_config_serializer=UpdateConfigRequestSchema()
    )
```

Manual start/stop:
```
temperature_value = uniform(1.6, 89.2)
humidity_value = uniform(1.6, 89.2)
temperature = DataPointFactory.create(sensor_id=1, value=f"{temperature_value:.2f}", timestamp=str(datetime.utcnow()))
humidity = DataPointFactory.create(sensor_id=2, value=f"{humidity_value:.2f}", timestamp=str(datetime.utcnow()))
device.data = [temperature, humidity]
device.start()
device.publish_data()
device.stop()
```

Using context manager:
```
with device:
    temperature_value = uniform(1.6, 89.2)
    humidity_value = uniform(1.6, 89.2)
    temperature = DataPointFactory.create(sensor_id=1, value=f"{temperature_value:.2f}", timestamp=str(datetime.utcnow()))
    humidity = DataPointFactory.create(sensor_id=2, value=f"{humidity_value:.2f}", timestamp=str(datetime.utcnow()))
    device.data = [temperature, humidity]
    device.publish_data()
```

Persist device configuration:
```
device_file_repository = DeviceFileRepository(filepath="device.yaml")
device_file_repository.save(device=device)
```

Load device configuration from file:
```
from os import environ

from knot_protocol import (
    DeviceFileRepository,
    DeviceFactory,
    DeviceEntity,
    SchemaFactory,
    EventFactory,
    DataPointFactory,
    ConfigurationFactory,
    KNoTValueType,
    DeviceRegistrationRequestSchema,
    DeviceAuthRequestSchema,
    DataPointsSchema,
    UpdateConfigRequestSchema,
    DeviceUnregistrationRequestDTO,
    amqp_data_management_setup,
    logger_factory)

device_file_repository = DeviceFileRepository(filepath="device.yaml")
device = device_file_repository.load()

logger = logger_factory()
KNOT_TOKEN = environ.get("KNOT_TOKEN")
DEVICE_ID = device.device_id

(
register_subscriber,
auth_subscriber,
update_config_subscriber,
register_publisher,
auth_publisher,
update_config_publisher,
data_publisher,
unregister_subscriber,
unregister_publisher,
amqp_generator) = amqp_data_management_setup(
    logger=logger,
    knot_token=KNOT_TOKEN,
    device_id=DEVICE_ID)

knot_device = DeviceFactory.configure_existing_device(
    device=device,
    amqp_generator=amqp_generator,
    register_subscriber=register_subscriber,
    register_publisher=register_publisher,
    register_serializer=DeviceRegistrationRequestSchema(),
    auth_publisher=auth_publisher,
    auth_subscriber=auth_subscriber,
    device_auth_serializer=DeviceAuthRequestSchema(),
    data_publisher=data_publisher,
    publisher_serializer=DataPointsSchema(),
    unregister_publisher=unregister_publisher,
    unregister_subscriber=unregister_subscriber,
    unregister_serializer=DeviceUnregistrationRequestDTO(),
    update_config_publisher=update_config_publisher,
    update_config_subscriber=update_config_subscriber,
    update_config_serializer=UpdateConfigRequestSchema()
    )
knot_device.start()
```

## Docker
```sh
$ sudo docker build --file docker/Dockerfile . --no-cache --tag knot_protocol
$ sudo docker run knot_protocol
```