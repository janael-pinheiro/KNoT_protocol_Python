from abc import ABC, abstractmethod
from knot_protocol_python.domain.entities.device_entity import DeviceEntity

class DeviceRepository(ABC):
    def save(self, device: DeviceEntity) -> None:
        ...

    def load(self) -> DeviceEntity:
        ...
