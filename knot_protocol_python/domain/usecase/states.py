from threading import Thread

from knot_protocol_python.domain.usecase.state import State
from knot_protocol_python.domain.boundary.input.subscriber import Subscriber
from knot_protocol_python.domain.boundary.output.publisher import Publisher
from knot_protocol_python.domain.boundary.output.DTO.registration_request_dto import RegistrationRequest
from knot_protocol_python.domain.boundary.output.DTO.authentication_request_dto import AuthenticationRequestDTO
from knot_protocol_python.domain.exceptions.device_exception import AlreadyRegisteredDeviceExcepiton, AuthenticationErrorException


class NewState(State):
    def __init__(
        self,
        device=None,
        wait_registration_state: State=None,
        publisher: Publisher = None,
        request_serializer = None) -> None:
        super().__init__(device)
        self.__wait_registration = wait_registration_state
        self.__publisher = publisher
        self.__request_serializer = request_serializer

    def handle(self) -> None:
        device = self.get_device()
        if not device.is_valid_device_id():
            device.device_id = device.create_id()
        device.transition_to_state(self.__wait_registration)
        self.set_device(device)
        wait_registration_thread = Thread(target=device.handle_state)
        wait_registration_thread.start()
        registration_request = RegistrationRequest(device.device_id, device.name)
        self.__publisher.content = str(self.__request_serializer.dumps(registration_request))
        self.__publisher.publish()

class WaitRegistrationState(State):
    def __init__(
        self,
        device=None,
        subscriber: Subscriber = None,
        registered_state: State = None,
        unregistered_state: State = None) -> None:
        super().__init__(device)
        self.subscriber = subscriber
        self.registered = registered_state
        self.unregisted = unregistered_state


    def handle(self) -> None:
        device = self.get_device()
        try:
            token = self.subscriber.subscribe()
            if token:
                device.token = token
                device.transition_to_state(self.registered)
            else:
                device.transition_to_state(self.unregisted)
        except AlreadyRegisteredDeviceExcepiton:
            device.transition_to_state(self.registered)
        self.set_device(device)


class RegisteredState(State):
    def __init__(
        self,
        device=None,
        publisher: Publisher = None, 
        request_serializer = None,
        wait_authentication_state: State = None) -> None:
        super().__init__(device)
        self.__wait_authentication = wait_authentication_state
        self.__publisher = publisher
        self.__request_serializer = request_serializer

    def handle(self) -> None:
        device = self.get_device()
        device.transition_to_state(self.__wait_authentication)
        self.set_device(device)
        wait_authentication_thread = Thread(target=device.handle_state)
        wait_authentication_thread.start()
        authentication_request = AuthenticationRequestDTO(device.device_id, device.token)
        self.__publisher.content = str(self.__request_serializer.dumps(authentication_request))
        self.__publisher.publish()


class UnregisteredState(State):
    def handle(self) -> None:
        ...


class WaitAuthenticateState(State):
    def __init__(
        self,
        device=None,
        subscriber: Subscriber = None,
        authenticated_state: State = None,
        unauthenticated_state: State = None) -> None:
        super().__init__(device)
        self.subscriber = subscriber
        self.authenticated = authenticated_state
        self.unauthenticated = unauthenticated_state

    def handle(self) -> None:
        device = self.get_device()
        try:
            self.subscriber.subscribe()
            device.transition_to_state(self.authenticated)
            print("Autenticated!")
        except AuthenticationErrorException:
            device.transition_to_state(self.unauthenticated)
        self.set_device(device)


class AuthenticatedState(State):
    def handle(self) -> None:
        ...


class UnauthenticatedState(State):
    def handle(self) -> None:
        ...


class WaitConfigState(State):
    def handle(self) -> None:
        ...


class ReadyState(State):
    def handle(self) -> None:
        ...


class PublishingState(State):
    def handle(self) -> None:
        ...
