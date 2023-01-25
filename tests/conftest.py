from knot_protocol_python.domain.DTO.data_point import DataPointDTO
from knot_protocol_python.domain.DTO.device_configuration import ConfigurationDTO
from knot_protocol_python.domain.entities.device_entity import DeviceEntity
from knot_protocol_python.domain.DTO.event import Event
from knot_protocol_python.domain.DTO.schema import Schema
from knot_protocol_python.domain.usecase.states import DisconnectedState, RegisteredState, UnregisteredState
from tests.mocks.subscriber_mock import ValidSubscriberMock, InvalidSubscriberMock, SubscriberWithExceptionMock
from tests.mocks.publisher_mock import RegisterPublisherMock
from knot_protocol_python.infraestructure.adapter.output.DTO.device_registration_request_DTO import DeviceRegistrationRequestDTO

import pytest


@pytest.fixture(scope="function")
def data_point() -> DataPointDTO:
    return DataPointDTO(sensor_id=1, value=42, timestamp="2023-01-21 12:15:00")


@pytest.fixture(scope="function")
def subscriber_with_valid_token():
    return ValidSubscriberMock()


@pytest.fixture(scope="function")
def subscriber_with_invalid_token():
    return InvalidSubscriberMock()


@pytest.fixture(scope="function")
def subscriber_with_exception():
    return SubscriberWithExceptionMock()


@pytest.fixture(scope="function")
def register_publisher():
    return RegisterPublisherMock()


@pytest.fixture(scope="function")
def device_1(data_point, subscriber_with_valid_token, register_publisher) -> DeviceEntity:
    schema = Schema(type_id=65521, unit=0, value_type=3, name="temperature")
    event = Event(change=True, time_seconds=5, lower_threshold=4, upper_threshold=10)
    configuration = ConfigurationDTO(event=event, schema=schema, sensor_id=1)
    registered_state = RegisteredState()
    new_state = DisconnectedState(
        registered_state=registered_state,
        register_publisher=register_publisher,
        register_subscriber=subscriber_with_valid_token,
        register_serializer=DeviceRegistrationRequestDTO())
    device = DeviceEntity(
        device_id="1",
        name="device_test",
        config=[configuration],
        state=new_state,
        data_points=[data_point],
        error="")
    return device


@pytest.fixture(scope="function")
def device_with_invalid_token(
        data_point,
        subscriber_with_invalid_token,
        register_publisher) -> DeviceEntity:
    configuration = ConfigurationDTO(event=None, schema=None, sensor_id=1)
    registered_state = RegisteredState()
    new_state = DisconnectedState(
        register_publisher=register_publisher,
        register_subscriber=subscriber_with_invalid_token,
        registered_state=registered_state,
        register_serializer=DeviceRegistrationRequestDTO())
    device = DeviceEntity(
        device_id="1",
        name="device_test",
        config=[configuration],
        state=new_state,
        data_points=[data_point],
        error="")
    return device


@pytest.fixture(scope="function")
def device_with_subscriber_exception(
        data_point,
        subscriber_with_exception,
        register_publisher) -> DeviceEntity:
    configuration = ConfigurationDTO(event=None, schema=None, sensor_id=1)
    registered_state = RegisteredState()
    new_state = DisconnectedState(
        register_publisher=register_publisher,
        register_subscriber=subscriber_with_exception,
        registered_state=registered_state,
        register_serializer=DeviceRegistrationRequestDTO())
    device = DeviceEntity(
        device_id="1",
        name="device_test",
        config=[configuration],
        state=new_state,
        data_points=[data_point],
        error="")
    return device


@pytest.fixture(scope="function")
def device_2(data_point) -> DeviceEntity:
    configuration = ConfigurationDTO(event=None, schema=None, sensor_id=1)
    return DeviceEntity(
        device_id="2",
        name="device_test",
        config=[configuration],
        state=DisconnectedState(),
        data_points=[data_point],
        error="")
