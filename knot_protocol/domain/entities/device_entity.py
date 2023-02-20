import uuid
from dataclasses import dataclass
from re import search
from time import sleep
from typing import List, Any

from knot_protocol.domain.boundary.output.DTO.data_point import DataPointDTO
from knot_protocol.domain.boundary.output.DTO.device_configuration import ConfigurationDTO
from knot_protocol.domain.usecase.state import State
from knot_protocol.domain.usecase.states import (AuthenticatedState,
                                                        ReadyState,
                                                        RegisteredState,
                                                        UpdatedSchemaState)
from knot_protocol.infrastructure.utils.knot_amqp_options import KNoTPatterns
from knot_protocol.infrastructure.utils.logger import logger_factory

logger = logger_factory()


@dataclass(eq=False)
class DeviceEntity:
    device_id: str
    name: str
    config: List[ConfigurationDTO]
    state: State
    amqp_generator: Any = None
    data: List[DataPointDTO] = None
    error: str = ""
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

    def __enter__(self) -> None:
        self.start()

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        self.stop()

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
        print("started")
        while not isinstance(self.state, ReadyState):
            try:
                self.register()
            except Exception as e:
                logger.error(str(e))
            if isinstance(self.state, RegisteredState):
                logger.info("Registered!")
                self.authenticate()
            if isinstance(self.state, AuthenticatedState):
                logger.info("Authenticated!")
                self.update_schema()
            if isinstance(self.state, UpdatedSchemaState):
                logger.info("Updated schema!")
                self.publish_data()
            sleep(1)

    def stop(self) -> None:
        try:
            next(self.amqp_generator)
        except StopIteration:
            print("Stopping device.")

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
            KNoTPatterns.TOKEN.value, self.token)
        return self.token != "" and token_regular_expression

    @classmethod
    def create_id(cls):
        return str(uuid.uuid4()).replace('-', '')[:cls.__id_length]
