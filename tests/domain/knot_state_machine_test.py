from unittest.mock import patch
import pytest

from knot_protocol_python.domain.usecase.states import NewState, RegisteredState, UnregisteredState


def test_device_handle_state_method(device_1):
    with patch.object(NewState, "handle") as mocked_state:
        device_1.handle_state()
    assert mocked_state.assert_called_once

def test_given_valid_token_transition_to_registered_state(device_1):
    assert isinstance(device_1.state, NewState)
    device_1.handle_state()
    assert isinstance(device_1.state, RegisteredState)
    assert device_1.token != ""


def test_given_invalid_token_transition_to_unregistered_state(device_with_invalid_token):
    assert isinstance(device_with_invalid_token.state, NewState)
    device_with_invalid_token.handle_state()
    assert isinstance(device_with_invalid_token.state, UnregisteredState)
    assert device_with_invalid_token.token == ""

def test_given_subscriber_exception_transition_to_registered_state(device_with_subscriber_exception):
    assert isinstance(device_with_subscriber_exception.state, NewState)
    device_with_subscriber_exception.handle_state()
    assert isinstance(device_with_subscriber_exception.state, RegisteredState)
