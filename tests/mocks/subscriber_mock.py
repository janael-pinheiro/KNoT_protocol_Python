from dataclasses import dataclass
from typing import Any

from knot_protocol_python.infraestructure.adapter.input.subscriber import AMQPCallback
from knot_protocol_python.domain.boundary.input.subscriber import Subscriber
from knot_protocol_python.domain.exceptions.device_exception import (
    AlreadyRegisteredDeviceException,
    AuthenticationErrorException,
    UpdateConfigurationException)


@dataclass
class ValidSchemaCallback(AMQPCallback):
    config: Any = None

    def execute(self, channel, method, properties, body):
        return


class InvalidSchemaCallback(AMQPCallback):
    def execute(self, channel, method, properties, body):
        raise UpdateConfigurationException()


@dataclass
class ValidRegisterCallback(AMQPCallback):
    token: str = ""
    def execute(self, channel, method, properties, body):
        return ""


@dataclass
class ValidRegisterSubscriberMock(Subscriber):
    callback: AMQPCallback = None

    def subscribe(self):
        self.callback.token = "XPTO"
        return 

    def unsubscribe(self):
        return False


@dataclass
class InvalidRegisterSubscriberMock(Subscriber):
    callback: AMQPCallback = None

    def subscribe(self):
        return None
    def unsubscribe(self):
        return False

@dataclass
class RegisterSubscriberWithExceptionMock(Subscriber):
    callback: AMQPCallback = None

    def subscribe(self):
        raise AlreadyRegisteredDeviceException("Device already exists")
    def unsubscribe(self):
        return False


@dataclass
class ValidAuthSubscriberMock(Subscriber):
    callback: AMQPCallback = None

    def subscribe(self):
        return
    
    def unsubscribe(self):
        ...


@dataclass
class InvalidAuthSubscriberMock(Subscriber):
    callback: AMQPCallback = None

    def subscribe(self):
        raise AuthenticationErrorException()
    
    def unsubscribe(self):
        ...


@dataclass
class ValidUpdateSchemaSubscriberMock(Subscriber):
    callback: AMQPCallback = None

    def subscribe(self):
        self.callback.config = None
        return "XPTO"

    def unsubscribe(self):
        ...


@dataclass
class InvalidUpdateSchemaSubscriberMock(Subscriber):
    callback: AMQPCallback = None

    def subscribe(self):
        self.callback.config = None
        raise UpdateConfigurationException()

    def unsubscribe(self):
        ...
