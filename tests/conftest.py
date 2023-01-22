from knot_protocol_python.domain.DTO.data_point import DataPointDTO
from knot_protocol_python.domain.DTO.device_configuration import ConfigurationDTO
from knot_protocol_python.domain.entities.device_entity import DeviceEntity
from knot_protocol_python.domain.usecase.states import NewState, WaitRegistrationState, RegisteredState, UnregisteredState
from tests.mocks.subscriber_mock import ValidSubscriberMock, InvalidSubscriberMock, SubscriberWithExceptionMock
from tests.mocks.publisher_mock import RegisterPublisherMock
from knot_protocol_python.infraestructure.adapter.output.DTO.device_registration_request_DTO import DeviceRegistrationRequestDTO

import pytest


@pytest.fixture(scope="function")
def data_point() -> DataPointDTO:
    return DataPointDTO(sensorID=1, value=42, timestamp="2023-01-21 12:15:00")


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
    configuration = ConfigurationDTO(event=None, schema=None, sensor_id=1)
    registered_state = RegisteredState()
    unregistered_state = UnregisteredState()
    wait_registration_state = WaitRegistrationState(
        registered_state=registered_state,
        unregistered_state=unregistered_state,
        subscriber=subscriber_with_valid_token)
    new_state = NewState(
        wait_registration_state=wait_registration_state,
        publisher=register_publisher,
        request_serializer=DeviceRegistrationRequestDTO())
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
    unregistered_state = UnregisteredState()
    wait_registration_state = WaitRegistrationState(
        registered_state=registered_state,
        unregistered_state=unregistered_state,
        subscriber=subscriber_with_invalid_token)
    new_state = NewState(
        wait_registration_state=wait_registration_state,
        publisher=register_publisher,
        request_serializer=DeviceRegistrationRequestDTO())
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
    unregistered_state = UnregisteredState()
    wait_registration_state = WaitRegistrationState(
        registered_state=registered_state,
        unregistered_state=unregistered_state,
        subscriber=subscriber_with_exception)
    new_state = NewState(
        wait_registration_state=wait_registration_state,
        publisher=register_publisher,
        request_serializer=DeviceRegistrationRequestDTO())
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
        state=NewState(),
        data_points=[data_point],
        error="")
