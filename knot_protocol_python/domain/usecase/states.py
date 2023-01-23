from threading import Thread

from knot_protocol_python.domain.usecase.state import State
from knot_protocol_python.domain.boundary.input.subscriber import Subscriber
from knot_protocol_python.domain.boundary.output.publisher import Publisher
from knot_protocol_python.domain.boundary.output.DTO.registration_request_dto import RegistrationRequest
from knot_protocol_python.domain.boundary.output.DTO.authentication_request_dto import AuthenticationRequestDTO
from knot_protocol_python.domain.exceptions.device_exception import (
    AlreadyRegisteredDeviceExcepiton,
    AuthenticationErrorException,
    UpdateConfigurationException)
from knot_protocol_python.domain.boundary.output.DTO.update_config_request import UpdateConfigRequest
from knot_protocol_python.domain.boundary.output.DTO.publishing_data_dto import PublishingData


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

    def __repr__(self) -> str:
        return "new"


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

    def __repr__(self) -> str:
        return "waitResponseRegister"


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

    def __repr__(self) -> str:
        return "registered"


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
        except AuthenticationErrorException:
            device.transition_to_state(self.unauthenticated)
        self.set_device(device)

    def __repr__(self) -> str:
        return "waitResponseAuth"


class AuthenticatedState(State):
    def __init__(
        self,
        device=None,
        publisher: Publisher = None, 
        request_serializer = None,
        wait_configuration_state: State = None) -> None:
        super().__init__(device)
        self.__wait_configuration = wait_configuration_state
        self.__publisher = publisher
        self.__request_serializer = request_serializer

    def handle(self) -> None:
        device = self.get_device()
        device.transition_to_state(self.__wait_configuration)
        self.set_device(device)
        wait_configuration_thread = Thread(target=device.handle_state)
        wait_configuration_thread.start()
        config_request = UpdateConfigRequest(id=device.device_id, config=device.config)
        self.__publisher.content = str(self.__request_serializer.dumps(config_request))
        self.__publisher.publish()

    def __repr__(self) -> str:
        return "authenticated"


class UnauthenticatedState(State):
    def handle(self) -> None:
        ...


class WaitConfigState(State):
    def __init__(
        self,
        device=None,
        subscriber: Subscriber = None,
        ready_state: State = None) -> None:
        super().__init__(device)
        self.subscriber = subscriber
        self.ready = ready_state

    def handle(self) -> None:
        device = self.get_device()
        try:
            config = self.subscriber.subscribe()
            if config:
                device.config = config
            device.transition_to_state(self.ready)
        except UpdateConfigurationException:
            print("Update configuration error!")
        self.set_device(device)

    def __repr__(self) -> str:
        return "waitResponseConfig"


class ReadyState(State):
    def __init__(
        self,
        device=None,
        publisher: Publisher = None, 
        publisher_serializer = None,
        publishing_state: State = None) -> None:
        super().__init__(device)
        self.__publishing_state = publishing_state
        self.__publisher = publisher
        self.__publisher_serializer = publisher_serializer

    def handle(self) -> None:
        device = self.get_device()
        data = PublishingData(id=device.device_id, data=device.data_points)
        serialized_data = str(self.__publisher_serializer.dumps(data))
        self.__publisher.content = serialized_data
        self.__publisher.publish()
        self.set_device(device)

    def __repr__(self) -> str:
        return "readyToSendData"


class PublishingState(State):
    def handle(self) -> None:
        ...
