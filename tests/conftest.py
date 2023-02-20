import pytest

from knot_protocol.domain.boundary.output.DTO.data_point import DataPointDTO
from knot_protocol.domain.boundary.output.DTO.schema import SchemaDTO
from knot_protocol.domain.boundary.output.DTO.event import Event
from knot_protocol.domain.boundary.output.DTO.device_configuration import ConfigurationDTO
from knot_protocol.domain.entities.device_entity import DeviceEntity
from knot_protocol.domain.usecase.states import (
    AuthenticatedState,
    DisconnectedState,
    RegisteredState,
    UpdatedSchemaState)
from knot_protocol.infrastructure.adapter.output.DTO.device_auth_request_DTO import \
    DeviceAuthRequestSchema
from knot_protocol.infrastructure.adapter.output.DTO.device_schema import \
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
                                         ValidRegisterCallback,
                                         ValidAuthCallback)
from tests.mocks.common_operation_mock import CommonOperationMock


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
    callback = ValidAuthCallback()
    valid_auth_subscriber_mock = ValidAuthSubscriberMock()
    valid_auth_subscriber_mock.callback = callback
    return valid_auth_subscriber_mock


@pytest.fixture(scope="function")
def invalid_auth_subscriber():
    callback = ValidAuthCallback()
    invalid_subscriber = InvalidAuthSubscriberMock()
    invalid_subscriber.callback = callback
    return invalid_subscriber


@pytest.fixture(scope="function")
def common_operation_mock():
    return CommonOperationMock(register_state=None, device=None)


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
def test_disconnected_state(publisher_mock, common_operation_mock):
    new_state = DisconnectedState(
        registered_state=RegisteredState(
            authenticated=None,
            publisher=None,
            request_serializer=None,
            subscriber=None,
            common_operation=common_operation_mock),
        authenticate_publisher=None,
        authenticate_serializer=None,
        authenticate_subscriber=None,
        authenticated=None,
        common_operation=common_operation_mock)
    return new_state


@pytest.fixture(scope="function")
def another_device(data_point, test_empty_disconnected_state, test_schema) -> DeviceEntity:
    return DeviceEntity(
        device_id="2",
        name="device_test",
        config=[test_schema],
        state=test_empty_disconnected_state,
        data=[data_point],
        error="")


@pytest.fixture(scope="function")
def test_registered_state(publisher_mock, common_operation_mock, valid_auth_subscriber):
    registered_state = RegisteredState(
        authenticated=AuthenticatedState(
            publisher=None,
            request_serializer=None,
            subscriber=None,
            updated_schema_state=None,
            common_operation=common_operation_mock),
        publisher=publisher_mock,
        request_serializer=DeviceAuthRequestSchema(),
        subscriber=valid_auth_subscriber,
        common_operation=common_operation_mock)
    return registered_state


@pytest.fixture(scope="function")
def test_authenticated_state(publisher_mock, common_operation_mock):
    authenticated = AuthenticatedState(
        publisher=publisher_mock,
        subscriber=subscriber_with_valid_token,
        request_serializer=DeviceSchema(),
        updated_schema_state=UpdatedSchemaState(ready_state=None, common_operation=common_operation_mock),
        common_operation=common_operation_mock)
    return authenticated


@pytest.fixture(scope="function")
def test_schema():
    schema = ConfigurationDTO(
        event=Event(change=True, time_seconds=5, lower_threshold=1, upper_threshold=10),
        schema=SchemaDTO(name="temperature", value_type=3, type_id=65521, unit=0),
        sensor_id=1)
    return schema



@pytest.fixture(scope="function")
def test_empty_disconnected_state(common_operation_mock):
    return DisconnectedState(
            authenticate_publisher=None,
            authenticate_subscriber=None,
            registered_state=None,
            authenticated=None,
            authenticate_serializer=None,
            common_operation=common_operation_mock,
            )


@pytest.fixture(scope="function")
def test_device(test_schema, test_empty_disconnected_state):
    device = DeviceEntity(
        device_id="1",
        name="device_test",
        config=[test_schema],
        state=test_empty_disconnected_state,
        data=[data_point],
        error="",
        token="")
    return device

@pytest.fixture(scope="function")
def valid_device_schema():
    device_schema = {
        "id": "1964a231a4d14173",
        "name": "d8ea733a-a788-41ec-9be5-3426b252b66f",
        "error": "",
        "state": "disconnected",
        "token": "5b67ce6b-ef21-7013-3115-2d6297e1bd2b",
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
