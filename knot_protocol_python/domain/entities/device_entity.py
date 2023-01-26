import uuid
from dataclasses import dataclass
from re import search
from time import sleep
from typing import List

from knot_protocol_python.domain.DTO.data_point import DataPointDTO
from knot_protocol_python.domain.DTO.device_configuration import SchemaDTO
from knot_protocol_python.domain.usecase.state import State
from knot_protocol_python.domain.usecase.states import (AuthenticatedState,
                                                        ReadyState,
                                                        RegisteredState,
                                                        UpdatedSchemaState)


@dataclass(eq=False)
class DeviceEntity:
    device_id: str
    name: str
    config: List[SchemaDTO]
    state: State
    data_points: List[DataPointDTO]
    error: str
    token: str = ""
    __id_length: int = 16

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

    def register(self) -> None:
        self.state.register()

    def unregister(self) -> None:
        self.state.unregister()

    def authenticate(self) -> None:
        self.state.authenticate()

    def update_schema(self) -> None:
        self.state.update_schema()

    def publish_data(self) -> None:
        self.state.publish_data()

    def start(self) -> None:
        while not isinstance(self.state, ReadyState):
            self.register()
            if isinstance(self.state, RegisteredState):
                print("Registered!!")
                self.authenticate()
            if isinstance(self.state, AuthenticatedState):
                print("Authenticated!")
                self.update_schema()
            if isinstance(self.state, UpdatedSchemaState):
                print("Updated schema!")
                self.publish_data()
            sleep(1)

    def is_valid_device_id(self) -> bool:
        if len(self.device_id) != 16:
            return False
        try:
            int(self.device_id, 16)
        except ValueError:
            return False
        return True

    def is_valid_token(self) -> bool:
        if self.token is None:
            return False
        token_regular_expression = search(
            "[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", self.token)
        return self.token != "" and token_regular_expression

    @classmethod
    def create_id(cls):
        return str(uuid.uuid4()).replace('-', '')[:cls.__id_length]
