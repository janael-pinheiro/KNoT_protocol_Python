import pytest
from marshmallow.exceptions import ValidationError

from knot_protocol.infrastructure.adapter.output.DTO.device_schema import DeviceSchema, SensorEvent, DataPointSchema, SensorSchema
from knot_protocol.domain.boundary.output.DTO.event import Event
from knot_protocol.domain.boundary.output.DTO.data_point import DataPointDTO
from knot_protocol.domain.boundary.output.DTO.schema import SchemaDTO


def test_given_device_entity_serialize(test_device, valid_device_schema):
    device_schema = DeviceSchema()
    serialized_device_configuration = device_schema.dump(test_device)
    assert valid_device_schema["config"][0]["event"]["upperThreshold"] == serialized_device_configuration["config"][0]["event"]["upperThreshold"]
    assert valid_device_schema["config"][0]["schema"]["name"] == serialized_device_configuration["config"][0]["schema"]["name"]


def test_given_valid_device_schema_return_entity(valid_device_schema):
    device_schema = DeviceSchema()
    device = device_schema.load(valid_device_schema)
    assert device.device_id == "1964a231a4d14173"


@pytest.mark.parametrize("invalid_id", ["1234567891abcde", "1234567891abcdeh", "12345", ""])
def test_given_device_schema_with_invalid_id_raise_exception(valid_device_schema, invalid_id):
    valid_device_schema["id"] = invalid_id
    device_schema = DeviceSchema()
    with pytest.raises(ValidationError):
        device_schema.load(valid_device_schema)


def test_given_valid_event_schema_return_entity(valid_event_configuration):
    event = SensorEvent().load(valid_event_configuration)
    assert isinstance(event, Event)

@pytest.mark.parametrize("invalid_change", ["a", "123"])
def test_given_event_schema_with_invalid_change_argument_raise_exception(valid_event_configuration, invalid_change):
    valid_event_configuration["change"] = invalid_change
    with pytest.raises(ValidationError):
        event = SensorEvent().load(valid_event_configuration)
        print(event)


@pytest.mark.parametrize("valid_sensor_id", ["1", "123", 984, 23, 8])
def test_given_sensor_configuration_with_valid_sensor_id_success(valid_data_point_configuration, valid_sensor_id):
    valid_data_point_configuration["sensorId"] = valid_sensor_id
    data_point = DataPointSchema().load(valid_data_point_configuration)
    assert isinstance(data_point, DataPointDTO)


@pytest.mark.parametrize("invalid_sensor_id", ["-1", "12.3", "98.4", "a", "sensor1"])
def test_given_sensor_configuration_with_invalid_sensor_id_raise_exception(valid_data_point_configuration, invalid_sensor_id):
    valid_data_point_configuration["sensorId"] = invalid_sensor_id
    with pytest.raises(ValidationError):
        DataPointSchema().load(valid_data_point_configuration)


def test_given_valid_sensor_schema_return_success(valid_sensor_schema):
    sensor_schema = SensorSchema().load(valid_sensor_schema)
    assert isinstance(sensor_schema, SchemaDTO)


@pytest.mark.parametrize("invalid_value_type", [5, "xpto", 453])
def test_given_invalid_value_type_raises_exception(
    valid_sensor_schema,
    invalid_value_type):
    valid_sensor_schema["valueType"] = invalid_value_type
    with pytest.raises(ValidationError):
        SensorSchema().load(valid_sensor_schema)
