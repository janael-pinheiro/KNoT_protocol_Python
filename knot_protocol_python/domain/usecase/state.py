from abc import ABC, abstractmethod


class State(ABC):
    def __init__(self, device = None) -> None:
        self.device = device

    @abstractmethod
    def register(self) -> None:
        ...

    def unregister(self) -> None:
        device = self.get_device()
        if not device.is_valid_token():
            return
        if not device.is_valid_device_id():
            return
        # unregister logic
        self.set_device(device)

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
