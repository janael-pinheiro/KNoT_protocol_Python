from dataclasses import dataclass
from typing import Any

from knot_protocol.infrastructure.adapter.input.subscriber import AMQPCallback
from knot_protocol.domain.boundary.input.subscriber import Subscriber
from knot_protocol.domain.exceptions.device_exception import (
    AlreadyRegisteredDeviceException,
    AuthenticationErrorException,
    UpdateConfigurationException)


@dataclass
class ValidSchemaCallback(AMQPCallback):
    config: Any = None

    def execute(self, channel, method, properties, body, queue_name):
        return


class InvalidSchemaCallback(AMQPCallback):
    def execute(self, channel, method, properties, body, queue_name):
        raise UpdateConfigurationException()


@dataclass
class ValidRegisterCallback(AMQPCallback):
    token: str = ""
    def execute(self, channel, method, properties, body, queue_name):
        return ""


@dataclass
class ValidAuthCallback(AMQPCallback):
    device_id: str = ""
    def execute(self, channel, method, properties, body, queue_name):
        return ""


@dataclass
class ValidRegisterSubscriberMock(Subscriber):
    callback: AMQPCallback = None

    def __enter__(self) -> None:
        ...

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        ...

    def subscribe(self):
        self.callback.token = "5b67ce6b-ef21-7013-3115-2d6297e1bd2b"

    def unsubscribe(self):
        return False


@dataclass
class InvalidRegisterSubscriberMock(Subscriber):
    callback: AMQPCallback = None

    def __enter__(self) -> None:
        ...

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        ...

    def subscribe(self):
        return None
    def unsubscribe(self):
        return False

@dataclass
class RegisterSubscriberWithExceptionMock(Subscriber):
    callback: AMQPCallback = None

    def __enter__(self) -> None:
        ...

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        ...

    def subscribe(self):
        raise AlreadyRegisteredDeviceException("Device already exists")
    def unsubscribe(self):
        return False


@dataclass
class ValidAuthSubscriberMock(Subscriber):
    callback: AMQPCallback = None

    def __enter__(self) -> None:
        ...

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        ...

    def subscribe(self):
        return

    def unsubscribe(self):
        ...


@dataclass
class InvalidAuthSubscriberMock(Subscriber):
    callback: AMQPCallback = None

    def __enter__(self) -> None:
        ...

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        ...

    def subscribe(self):
        raise AuthenticationErrorException()

    def unsubscribe(self):
        ...


@dataclass
class ValidUpdateSchemaSubscriberMock(Subscriber):
    callback: AMQPCallback = None

    def __enter__(self) -> None:
        ...

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        ...

    def subscribe(self):
        self.callback.config = None
        return "XPTO"

    def unsubscribe(self):
        ...


@dataclass
class InvalidUpdateSchemaSubscriberMock(Subscriber):
    callback: AMQPCallback = None

    def __enter__(self) -> None:
        ...

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        ...

    def subscribe(self):
        self.callback.config = None
        raise UpdateConfigurationException()

    def unsubscribe(self):
        ...
