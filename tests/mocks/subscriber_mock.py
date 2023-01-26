from knot_protocol_python.domain.boundary.input.subscriber import Subscriber
from knot_protocol_python.domain.exceptions.device_exception import (
    AlreadyRegisteredDeviceException,
    AuthenticationErrorException,
    UpdateConfigurationException)


class ValidRegisterSubscriberMock(Subscriber):
    def subscribe(self):
        return "XPTO"
    def unsubscribe(self):
        return False


class InvalidRegisterSubscriberMock(Subscriber):
    def subscribe(self):
        return None
    def unsubscribe(self):
        return False

class RegisterSubscriberWithExceptionMock(Subscriber):
    def subscribe(self):
        raise AlreadyRegisteredDeviceException("Device already exists")
    def unsubscribe(self):
        return False


class ValidAuthSubscriberMock(Subscriber):
    def subscribe(self):
        return
    
    def unsubscribe(self):
        ...


class InvalidAuthSubscriberMock(Subscriber):
    def subscribe(self):
        raise AuthenticationErrorException()
    
    def unsubscribe(self):
        ...


class ValidUpdateSchemaSubscriberMock(Subscriber):
    def subscribe(self):
        return "XPTO"

    def unsubscribe(self):
        ...


class InvalidUpdateSchemaSubscriberMock(Subscriber):
    def subscribe(self):
        raise UpdateConfigurationException()

    def unsubscribe(self):
        ...
