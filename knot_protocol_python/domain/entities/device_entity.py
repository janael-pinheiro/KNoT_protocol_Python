from dataclasses import dataclass
from typing import List
import uuid


from knot_protocol_python.domain.DTO.device_configuration import ConfigurationDTO
from knot_protocol_python.domain.DTO.data_point import DataPointDTO
from knot_protocol_python.domain.usecase.state import State


@dataclass
class DeviceEntity:

    __id_length: int = 16

    def __init__(
        self,
        device_id: str,
        name: str,
        config: List[ConfigurationDTO],
        state: State,
        data_points: List[DataPointDTO],
        error: str,
        token: str = "") -> None:
        self.device_id = device_id
        self.name = name
        self.config = config
        self.error = error
        self.token = token
        self.data_points = data_points
        self.transition_to_state(state)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DeviceEntity):
            return False
        return other.device_id == self.device_id

    def __hash__(self) -> int:
        return hash(self.device_id)

    def __repr__(self) -> str:
        return f"Device {self.name} has ID {self.device_id}"

    def transition_to_state(self, state: State):
        self.state = state
        self.state.set_device(self)

    def handle_state(self) -> None:
        self.state.handle()

    def is_valid_device_id(self) -> bool:
        if len(self.device_id) != 16:
            return False
        try:
            int(self.device_id, 16)
        except ValueError:
            return False
        return True

    @classmethod
    def create_id(cls):
        return str(uuid.uuid4()).replace('-', '')[:cls.__id_length]
