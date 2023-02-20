from dataclasses import dataclass
from typing import Any

from knot_protocol.domain.usecase.states import CommonOperation, RegisteredState


@dataclass
class CommonOperationMock(CommonOperation):
    device: Any
    register_state: Any

    def unregister(self):
        ...

    def register(self):
        self.device.token = ""
        self.device.transition_to_state(self.register_state)
