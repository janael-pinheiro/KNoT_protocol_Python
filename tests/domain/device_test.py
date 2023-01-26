import pytest 

from knot_protocol_python.domain.DTO.data_point import DataPointDTO
from knot_protocol_python.domain.entities.device_entity import DeviceEntity


def test_given_two_data_points_with_same_values_then_equal(data_point):
    new_data_point = DataPointDTO(
        sensor_id=data_point.sensor_id,
        value=data_point.value,
        timestamp=data_point.timestamp)
    assert data_point == new_data_point


def test_given_two_with_different_ids_return_true(test_device, device_2):
    assert test_device != device_2


def test_device_id_must_sixteen_length():
    EXPECTED_LENGTH = 16
    device_id = DeviceEntity.create_id()
    assert EXPECTED_LENGTH == len(device_id)


def test_given_valid_device_id_return_true(test_device):
    device_id = DeviceEntity.create_id()
    test_device.device_id = device_id
    assert test_device.is_valid_device_id()


@pytest.mark.parametrize("device_id", ["daedev", "443d53d180bf4g-1", "m443d53d180bf4d1", ""])
def test_given_invalid_device_id_return_false(test_device, device_id):
    test_device.device_id = device_id
    assert not test_device.is_valid_device_id()


@pytest.mark.parametrize("token", [
    "c9303bab-53a4-4bff-9f5b-645fca22bcda",
    "a9303fab-53a4-4bff-9f5b-645fca22bcda",
    "d9e01bab-53a4-4bff-9f5b-64ffca22bcda"])
def test_given_valid_token_return_true(test_device, token):
    test_device.token = token
    assert test_device.is_valid_token()


@pytest.mark.parametrize("token", [
    "",
    None,
    "d9e01bab",
    "n9e01baf-r3a4-4bff-9f5b-64ffca22bcd"])
def test_given_invalid_token_return_false(test_device, token):
    test_device.token = token
    assert not test_device.is_valid_token()
