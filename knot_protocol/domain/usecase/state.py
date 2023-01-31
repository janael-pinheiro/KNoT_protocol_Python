from abc import ABC, abstractmethod


class State(ABC):
    def __init__(self, device = None) -> None:
        self.device = device

    @abstractmethod
    def register(self) -> None:
        ...

    @abstractmethod
    def unregister(self) -> None:
        ...

    @abstractmethod
    def authenticate(self) -> None:
        ...

    @abstractmethod
    def update_schema(self) -> None:
        ...

    @abstractmethod
    def publish_data(self) -> None:
        ...

    def get_device(self):
        return self.device

    def set_device(self, device):
        self.device = device
