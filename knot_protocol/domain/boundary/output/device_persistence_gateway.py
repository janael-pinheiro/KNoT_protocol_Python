from abc import ABC, abstractmethod

from knot_protocol.domain.entities.device_entity import DeviceEntity

class DevicePersistenceGateway(ABC):
    @abstractmethod
    def save(self, device: DeviceEntity) -> None:
        ...

    @abstractmethod
    def load(self) -> DeviceEntity:
        ...
