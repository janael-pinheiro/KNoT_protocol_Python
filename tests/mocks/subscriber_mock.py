from knot_protocol_python.domain.boundary.input.subscriber import Subscriber
from knot_protocol_python.domain.exceptions.device_exception import AlreadyRegisteredDeviceExcepiton

class ValidSubscriberMock(Subscriber):
    def subscribe(self):
        return "XPTO"
    def unsubscribe(self):
        return False


class InvalidSubscriberMock(Subscriber):
    def subscribe(self):
        return None
    def unsubscribe(self):
        return False

class SubscriberWithExceptionMock(Subscriber):
    def subscribe(self):
        raise AlreadyRegisteredDeviceExcepiton("Device already exists")
    def unsubscribe(self):
        return False
