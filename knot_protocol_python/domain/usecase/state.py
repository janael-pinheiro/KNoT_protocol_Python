from abc import ABC, abstractmethod


class State(ABC):
    def __init__(self, device = None) -> None:
        self.device = device

    @abstractmethod
    def handle(self) -> None:
        ...

    def get_device(self):
        return self.device

    def set_device(self, device):
        self.device = device
