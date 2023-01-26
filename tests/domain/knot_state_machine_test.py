from unittest.mock import patch
import pytest

from knot_protocol_python.domain.usecase.states import DisconnectedState, RegisteredState, AuthenticatedState, UpdatedSchemaState
from knot_protocol_python.domain.exceptions.device_exception import NotAuthenticatedException


def test_device_register_is_called(subscriber_with_valid_token,
    test_disconnected_state,
    test_device):
    test_disconnected_state.register_subscriber = subscriber_with_valid_token
    test_device.transition_to_state(test_disconnected_state)
    with patch.object(DisconnectedState, "register") as mocked_state:
        test_device.register()
    assert mocked_state.assert_called_once

def test_given_valid_token_transition_to_registered_state(
    subscriber_with_valid_token,
    test_disconnected_state,
    test_device
    ):
    test_disconnected_state.register_subscriber = subscriber_with_valid_token
    test_device.transition_to_state(test_disconnected_state)
    assert isinstance(test_device.state, DisconnectedState)
    test_device.register()
    assert isinstance(test_device.state, RegisteredState)
    assert test_device.token != ""


def test_given_invalid_token_remains_diconnected_state(
    subscriber_with_invalid_token,
    test_disconnected_state,
    test_device
    ):
    test_disconnected_state.authenticate_subscriber = subscriber_with_invalid_token
    test_device.transition_to_state(test_disconnected_state)
    assert isinstance(test_device.state, DisconnectedState)
    test_device.authenticate()
    assert isinstance(test_device.state, DisconnectedState)
    assert test_device.token == ""


def test_given_disconnected_device_when_publish_data_raises_not_authenticated_exception(
    subscriber_with_valid_token,
    test_disconnected_state,
    test_device
    ):
    test_disconnected_state.register_subscriber = subscriber_with_valid_token
    test_device.transition_to_state(test_disconnected_state)
    with pytest.raises(NotAuthenticatedException):
        test_device.publish_data()


def test_given_subscriber_exception_transition_to_registered_state(
    test_disconnected_state,
    subscriber_with_exception,
    test_device):
    test_disconnected_state.register_subscriber = subscriber_with_exception
    test_device.transition_to_state(test_disconnected_state)
    assert isinstance(test_device.state, DisconnectedState)
    test_device.register()
    assert isinstance(test_device.state, RegisteredState)

def test_given_valid_auth_subscriber_when_device_registered_then_transition_to_authenticated(
    valid_auth_subscriber,
    test_registered_state,
    test_device):
    test_registered_state.subscriber = valid_auth_subscriber
    test_device.transition_to_state(test_registered_state)
    assert isinstance(test_device.state, RegisteredState)
    test_device.authenticate()
    assert isinstance(test_device.state, AuthenticatedState)


def test_given_invalid_auth_subscriber_when_device_registered_then_remains_registered(
    invalid_auth_subscriber,
    test_registered_state,
    test_device
    ):
    test_registered_state.subscriber = invalid_auth_subscriber
    test_device.transition_to_state(test_registered_state)
    assert isinstance(test_device.state, RegisteredState)
    test_device.authenticate()
    assert isinstance(test_device.state, RegisteredState)


def test_given_valid_schema_subscriber_when_device_authenticated_then_transition_to_updated_schema(
    test_authenticated_state,
    valid_update_schema_subscriber_mock,
    test_device
    ):
    test_authenticated_state.subscriber = valid_update_schema_subscriber_mock
    test_device.transition_to_state(test_authenticated_state)
    assert isinstance(test_device.state, AuthenticatedState)
    test_device.update_schema()
    assert isinstance(test_device.state, UpdatedSchemaState)


def test_given_invalid_schema_subscriber_when_device_authenticated_then_transition_to_updated_schema(
    test_authenticated_state,
    invalid_update_schema_subscriber_mock,
    test_device):
    test_authenticated_state.subscriber = invalid_update_schema_subscriber_mock
    test_device.transition_to_state(test_authenticated_state)
    assert isinstance(test_device.state, AuthenticatedState)
    test_device.update_schema()
    assert isinstance(test_device.state, AuthenticatedState)

