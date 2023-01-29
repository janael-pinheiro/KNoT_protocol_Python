from knot_protocol.domain.entities.device_entity import DeviceEntity
from knot_protocol.domain.usecase.states import PublishingState


class KNoTThingManager:
    def __init__(
            self,
            device: DeviceEntity,) -> None:
        self.__device = device

    def start(self) -> None:
        self.__turn_on_device()

    def __turn_on_device(self) -> None:
        while not isinstance(self.__device.state, PublishingState):
            self.__device.stateg_handle()
