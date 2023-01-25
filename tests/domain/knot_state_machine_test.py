from unittest.mock import patch
import pytest

from knot_protocol_python.domain.usecase.states import DisconnectedState, RegisteredState, UnregisteredState


def test_device_handle_state_method(device_1):
    with patch.object(DisconnectedState, "register") as mocked_state:
        device_1.register()
    assert mocked_state.assert_called_once

def test_given_valid_token_transition_to_registered_state(device_1):
    assert isinstance(device_1.state, DisconnectedState)
    device_1.register()
    assert isinstance(device_1.state, RegisteredState)
    assert device_1.token != ""


def test_given_invalid_token_transition_to_unregistered_state(device_with_invalid_token):
    assert isinstance(device_with_invalid_token.state, DisconnectedState)
    device_with_invalid_token.register()
    assert isinstance(device_with_invalid_token.state, DisconnectedState)
    assert device_with_invalid_token.token == ""

def test_given_subscriber_exception_transition_to_registered_state(device_with_subscriber_exception):
    assert isinstance(device_with_subscriber_exception.state, DisconnectedState)
    device_with_subscriber_exception.register()
    assert isinstance(device_with_subscriber_exception.state, RegisteredState)
