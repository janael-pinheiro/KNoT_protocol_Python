from abc import ABC, abstractmethod


class Subscriber(ABC):
    @abstractmethod
    def subscribe(self):
        ...
    
    @abstractmethod
    def unsubscribe(self):
        ...