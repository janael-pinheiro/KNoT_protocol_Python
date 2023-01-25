from threading import Thread

from knot_protocol_python.domain.usecase.state import State
from knot_protocol_python.domain.boundary.input.subscriber import Subscriber
from knot_protocol_python.domain.boundary.output.publisher import Publisher
from knot_protocol_python.domain.boundary.output.DTO.registration_request_dto import RegistrationRequest
from knot_protocol_python.domain.boundary.output.DTO.authentication_request_dto import AuthenticationRequestDTO
from knot_protocol_python.domain.exceptions.device_exception import (
    AlreadyRegisteredDeviceException,
    AuthenticationErrorException,
    UpdateConfigurationException,
    AlreadyAuthenticatedException,
    AlreadyUpdatedSchema,
    NotReadyException,
    NotRegistered,
    NotAuthenticatedException,
    AlreadyReady)
from knot_protocol_python.domain.boundary.output.DTO.update_config_request import UpdateConfigRequest
from knot_protocol_python.domain.boundary.output.DTO.publishing_data_dto import PublishingData


class DisconnectedState(State):
    def __init__(
        self,
        device=None,
        register_subscriber: Subscriber = None,
        register_publisher: Publisher = None,
        authenticate_subscriber: Subscriber = None,
        authenticate_publisher: Publisher = None,
        registered_state: State = None,
        authenticated: State = None,
        register_serializer = None,
        authenticate_serializer = None) -> None:
        super().__init__(device)
        self.__registered = registered_state
        self.__authenticated = authenticated
        self.__register_publisher = register_publisher
        self.__register_subscriber = register_subscriber
        self.__authenticate_publisher = authenticate_publisher
        self.__authenticate_subscriber = authenticate_subscriber
        self.__register_serializer = register_serializer
        self.__authenticate_serializer = authenticate_serializer

    def register(self) -> None:
        device = self.get_device()
        if not device.is_valid_device_id():
            device.device_id = device.create_id()
        if not device.is_valid_token():
            registration_request = RegistrationRequest(device.device_id, device.name)
            self.__register_publisher.content = str(self.__register_serializer.dumps(registration_request))
            self.__register_publisher.publish()
            try:
                token = self.__register_subscriber.subscribe()
                if token:
                    device.token = token
                    device.transition_to_state(self.__registered)
            except AlreadyRegisteredDeviceException:
                device.transition_to_state(self.__registered)
        self.set_device(device)

    def authenticate(self) -> None:
        device = self.get_device()
        if not device.is_valid_token():
            return
        if not device.is_valid_device_id():
            return
        authentication_request = AuthenticationRequestDTO(device.device_id, device.token)
        self.__authenticate_publisher.content = str(self.__authenticate_serializer.dumps(authentication_request))
        self.__authenticate_publisher.publish()
        try:
            self.__authenticate_subscriber.subscribe()
            device.transition_to_state(self.__authenticated)
        except AuthenticationErrorException:
            ...
        self.set_device(device)

    def update_schema(self) -> None:
        raise NotRegistered()

    def publish_data(self) -> None:
        raise NotRegistered()

    def __repr__(self) -> str:
        return "new"


class RegisteredState(State):
    def __init__(
        self,
        device=None,
        publisher: Publisher = None,
        subscriber: Subscriber = None,
        request_serializer = None,
        authenticated: State = None) -> None:
        super().__init__(device)
        self.__publisher = publisher
        self.__subscriber = subscriber
        self.__request_serializer = request_serializer
        self.__authenticated = authenticated

    def register(self) -> None:
        raise AlreadyRegisteredDeviceException()

    def authenticate(self) -> None:
        device = self.get_device()
        authentication_request = AuthenticationRequestDTO(device.device_id, device.token)
        self.__publisher.content = str(self.__request_serializer.dumps(authentication_request))
        self.__publisher.publish()
        try:
            self.__subscriber.subscribe()
            device.transition_to_state(self.__authenticated)
        except AuthenticationErrorException:
            ...
        self.set_device(device)

    def update_schema(self) -> None:
        raise NotAuthenticatedException()

    def publish_data(self) -> None:
        raise NotAuthenticatedException()

    def __repr__(self) -> str:
        return "registered"


class UnregisteredState(State):
    def __init__(
        self,
        device=None,
        publisher: Publisher = None,
        register_serializer = None,
        registered: State = None) -> None:
        super().__init__(device)
        self.__publisher = publisher
        self.__request_serializer = register_serializer
        self.__registered = registered

    def register(self) -> None:
        raise AlreadyRegisteredDeviceException()

    def authenticate(self) -> None:
        raise NotRegistered()

    def update_schema(self) -> None:
        raise NotRegistered()

    def publish_data(self) -> None:
        raise NotRegistered()

    def __repr__(self) -> str:
        return "registered"


class AuthenticatedState(State):
    def __init__(
        self,
        device=None,
        publisher: Publisher = None,
        subscriber: Subscriber = None,
        request_serializer = None,
        updated_schema_state: State = None) -> None:
        super().__init__(device)
        self.__publisher = publisher
        self.__subscriber = subscriber
        self.__request_serializer = request_serializer
        self.__updated_schema = updated_schema_state

    def register(self) -> None:
        raise AlreadyRegisteredDeviceException()

    def authenticate(self) -> None:
        raise AlreadyAuthenticatedException()

    def update_schema(self) -> None:
        device = self.get_device()
        config_request = UpdateConfigRequest(id=device.device_id, config=device.config)
        self.__publisher.content = str(self.__request_serializer.dumps(config_request))
        self.__publisher.publish()
        try:
            config = self.__subscriber.subscribe()
            if config:
                device.config = config
            device.transition_to_state(self.__updated_schema)
        except UpdateConfigurationException:
            ...
        self.set_device(device)

    def publish_data(self) -> None:
        raise NotReadyException()

    def __repr__(self) -> str:
        return "authenticated"


class UpdatedSchemaState(State):
    def __init__(
        self,
        device=None,
        ready_state: State = None) -> None:
        super().__init__(device)
        self.__ready = ready_state

    def register(self) -> None:
        raise AlreadyRegisteredDeviceException()

    def authenticate(self) -> None:
        raise AlreadyAuthenticatedException()

    def update_schema(self) -> None:
        raise AlreadyUpdatedSchema()

    def publish_data(self) -> None:
        device = self.get_device()
        device.transition_to_state(self.__ready)
        device.publish_data()
        self.set_device(device)

    def __repr__(self) -> str:
        return "updatedSchema"

class ReadyState(State):
    def __init__(
        self,
        device=None,
        publisher: Publisher = None,
        publisher_serializer = None) -> None:
        super().__init__(device)
        self.__publisher = publisher
        self.__publisher_serializer = publisher_serializer

    def register(self) -> None:
        raise AlreadyReady()

    def authenticate(self) -> None:
        raise AlreadyReady()

    def update_schema(self) -> None:
        raise AlreadyReady()

    def publish_data(self) -> None:
        device = self.get_device()
        data = PublishingData(id=device.device_id, data=device.data_points)
        serialized_data = str(self.__publisher_serializer.dumps(data))
        self.__publisher.content = serialized_data
        self.__publisher.publish()
        self.set_device(device)

    def __repr__(self) -> str:
        return "readyToSendData"
