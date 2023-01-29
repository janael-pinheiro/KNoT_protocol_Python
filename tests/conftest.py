import pytest

from knot_protocol.domain.DTO.data_point import DataPointDTO
from knot_protocol.domain.DTO.schema import SchemaDTO
from knot_protocol.domain.DTO.event import Event
from knot_protocol.domain.DTO.device_configuration import ConfigurationDTO
from knot_protocol.domain.entities.device_entity import DeviceEntity
from knot_protocol.domain.usecase.states import (AuthenticatedState,
                                                        DisconnectedState,
                                                        RegisteredState,
                                                        UpdatedSchemaState)
from knot_protocol.infraestructure.adapter.output.DTO.device_auth_request_DTO import \
    DeviceAuthRequestDTO
from knot_protocol.infraestructure.adapter.output.DTO.device_registration_request_DTO import \
    DeviceRegistrationRequestDTO
from knot_protocol.infraestructure.adapter.output.DTO.device_schema import \
    DeviceSchema
from tests.mocks.publisher_mock import PublisherMock
from tests.mocks.subscriber_mock import (InvalidAuthSubscriberMock,
                                         InvalidRegisterSubscriberMock,
                                         InvalidUpdateSchemaSubscriberMock,
                                         RegisterSubscriberWithExceptionMock,
                                         ValidAuthSubscriberMock,
                                         ValidRegisterSubscriberMock,
                                         ValidUpdateSchemaSubscriberMock,
                                         ValidSchemaCallback,
                                         InvalidSchemaCallback,
                                         ValidRegisterCallback)


@pytest.fixture(scope="function")
def data_point() -> DataPointDTO:
    return DataPointDTO(sensor_id=1, value=42, timestamp="2023-01-21 12:15:00")


@pytest.fixture(scope="function")
def subscriber_with_valid_token():
    callback = ValidRegisterCallback()
    subscriber = ValidRegisterSubscriberMock()
    subscriber.callback = callback
    return subscriber


@pytest.fixture(scope="function")
def subscriber_with_invalid_token():
    return InvalidRegisterSubscriberMock()


@pytest.fixture(scope="function")
def subscriber_with_exception():
    return RegisterSubscriberWithExceptionMock()


@pytest.fixture(scope="function")
def valid_auth_subscriber():
    return ValidAuthSubscriberMock()


@pytest.fixture(scope="function")
def invalid_auth_subscriber():
    return InvalidAuthSubscriberMock()


@pytest.fixture(scope="function")
def valid_update_schema_subscriber_mock():
    callback = ValidSchemaCallback()
    subscriber = ValidUpdateSchemaSubscriberMock()
    subscriber.callback = callback
    return subscriber


@pytest.fixture(scope="function")
def invalid_update_schema_subscriber_mock():
    callback = InvalidSchemaCallback()
    subscriber = InvalidUpdateSchemaSubscriberMock()
    subscriber.callback = callback
    return subscriber


@pytest.fixture(scope="function")
def publisher_mock():
    return PublisherMock()


@pytest.fixture(scope="function")
def test_disconnected_state(publisher_mock):
    new_state = DisconnectedState(
        register_publisher=publisher_mock,
        register_subscriber=publisher_mock,
        registered_state=RegisteredState(
            authenticated=None,
            publisher=None,
            request_serializer=None,
            subscriber=None),
        register_serializer=DeviceRegistrationRequestDTO(),
        authenticate_publisher=None,
        authenticate_serializer=None,
        authenticate_subscriber=None,
        authenticated=None)
    return new_state


@pytest.fixture(scope="function")
def another_device(data_point, test_empty_disconnected_state) -> DeviceEntity:
    configuration = SchemaDTO(event=None, schema=None, sensor_id=1)
    return DeviceEntity(
        device_id="2",
        name="device_test",
        config=[configuration],
        state=test_empty_disconnected_state,
        data=[data_point],
        error="")


@pytest.fixture(scope="function")
def test_registered_state(publisher_mock):
    registered_state = RegisteredState(
        authenticated=AuthenticatedState(
            publisher=None,
            request_serializer=None,
            subscriber=None,
            updated_schema_state=None),
        publisher=publisher_mock,
        request_serializer=DeviceAuthRequestDTO(),
        subscriber=None)
    return registered_state


@pytest.fixture(scope="function")
def test_authenticated_state(publisher_mock):
    authenticated = AuthenticatedState(
        publisher=publisher_mock,
        subscriber=subscriber_with_valid_token,
        request_serializer=DeviceSchema(),
        updated_schema_state=UpdatedSchemaState(ready_state=None))
    return authenticated


@pytest.fixture(scope="function")
def test_schema():
    schema = ConfigurationDTO(
        event=Event(change=True, time_seconds=5, lower_threshold=1, upper_threshold=10),
        schema=SchemaDTO(name="temperature", value_type=3, type_id=65521, unit=0),
        sensor_id=1)
    return schema



@pytest.fixture(scope="function")
def test_empty_disconnected_state():
    return DisconnectedState(
            authenticate_publisher=None,
            register_subscriber=None,
            authenticate_serializer=None,
            authenticate_subscriber=None,
            authenticated=None,
            register_publisher=None,
            register_serializer=None,
            registered_state=None)


@pytest.fixture(scope="function")
def test_device(test_schema, test_empty_disconnected_state):
    device = DeviceEntity(
        device_id="1",
        name="device_test",
        config=[test_schema],
        state=test_empty_disconnected_state,
        data=[data_point],
        error="")
    return device

@pytest.fixture(scope="function")
def valid_device_schema():
    device_schema = {
        "id": "1964a231a4d14173",
        "name": "d8ea733a-a788-41ec-9be5-3426b252b66f",
        "error": "",
        "state": "disconnected",
        "config": [{
            "event": {
                "lowerThreshold": 4.0,
                "upperThreshold": 10.0,
                "change": True,
                "timeSec": 5},
            "schema": {
                "unit": 0,
                "name": "temperature",
                "valueType": 3,
                "typeId": 65521},
            "sensorId": 1}
            ]}
    return device_schema


@pytest.fixture(scope="function")
def valid_event_configuration():
    return {
        "change": True,
        "lowerThreshold": 47.0,
        "timeSec": 1,
        "upperThreshold": 154.0}


@pytest.fixture(scope="function")
def valid_data_point_configuration():
    return {
        "sensorId": 1,
        "value": 0,
        "timestamp": ""
    }


@pytest.fixture(scope="function")
def valid_sensor_schema():
    return {
        "typeId": 65521,
        "unit": 0,
        "valueType": 1,
        "name": "temperature"
    }
