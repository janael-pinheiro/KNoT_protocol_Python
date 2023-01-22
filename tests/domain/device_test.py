import pytest 

from knot_protocol_python.domain.DTO.data_point import DataPointDTO
from knot_protocol_python.domain.entities.device_entity import DeviceEntity


def test_given_two_data_points_with_same_values_then_equal(data_point):
    new_data_point = DataPointDTO(
        sensorID=data_point.sensorID,
        value=data_point.value,
        timestamp=data_point.timestamp)
    assert data_point == new_data_point


def test_given_two_with_different_ids_return_true(device_1, device_2):
    assert device_1 != device_2


def test_device_id_must_sixteen_length():
    EXPECTED_LENGTH = 16
    device_id = DeviceEntity.create_id()
    assert EXPECTED_LENGTH == len(device_id)


def test_given_valid_device_id_return_true(device_1):
    device_id = DeviceEntity.create_id()
    device_1.device_id = device_id
    assert device_1.is_valid_device_id()


@pytest.mark.parametrize("device_id", ["daedev", "443d53d180bf4g-1", "m443d53d180bf4d1", ""])
def test_given_invalid_device_id_return_false(device_1, device_id):
    device_1.device_id = device_id
    assert not device_1.is_valid_device_id()
