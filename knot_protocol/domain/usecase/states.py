from dataclasses import dataclass

from marshmallow import Schema

from knot_protocol.domain.boundary.input.subscriber import Subscriber
from knot_protocol.domain.boundary.output.DTO.authentication_request_dto import \
    AuthenticationRequestDTO
from knot_protocol.domain.boundary.output.DTO.publishing_data_dto import \
    PublishingData
from knot_protocol.domain.boundary.output.DTO.registration_request_dto import \
    RegistrationRequest
from knot_protocol.domain.boundary.output.DTO.update_config_request import \
    UpdateConfigRequest
from knot_protocol.domain.boundary.output.publisher import Publisher
from knot_protocol.domain.exceptions.device_exception import (
    AlreadyAuthenticatedException, AlreadyReady,
    AlreadyRegisteredDeviceException, AlreadyUpdatedSchema,
    AuthenticationErrorException, NotAuthenticatedException, NotReadyException,
    NotRegistered, UpdateConfigurationException)
from knot_protocol.domain.usecase.state import State


@dataclass
class DisconnectedState(State):
    register_subscriber: Subscriber
    register_publisher: Publisher
    authenticate_subscriber: Subscriber
    authenticate_publisher: Publisher
    registered_state: State
    authenticated: State
    register_serializer: Schema
    authenticate_serializer: Schema

    def register(self) -> None:
        device = self.get_device()
        if not device.is_valid_device_id():
            device.device_id = device.create_id()
        if not device.is_valid_token():
            registration_request = RegistrationRequest(device.device_id, device.name)
            self.register_publisher.content = str(self.register_serializer.dumps(registration_request))
            self.register_publisher.publish()
            self.register_subscriber.callback.device_id = device.device_id
            self.register_subscriber.subscribe()
            token = self.register_subscriber.callback.token
            if token:
                device.token = token
                device.transition_to_state(self.registered_state)
            return
        device.transition_to_state(self.registered_state)
        self.set_device(device)

    def authenticate(self) -> None:
        device = self.get_device()
        if not device.is_valid_token():
            return
        if not device.is_valid_device_id():
            return
        authentication_request = AuthenticationRequestDTO(device.device_id, device.token)
        self.authenticate_publisher.content = str(self.authenticate_serializer.dumps(authentication_request))
        self.authenticate_publisher.publish()
        try:
            self.authenticate_subscriber.callback.device_id = device.device_id
            self.authenticate_subscriber.subscribe()
            device.transition_to_state(self.authenticated_state)
        except AuthenticationErrorException:
            ...
        self.set_device(device)

    def update_schema(self) -> None:
        raise NotAuthenticatedException()

    def publish_data(self) -> None:
        raise NotAuthenticatedException()

    def __repr__(self) -> str:
        return "disconnected"


@dataclass
class RegisteredState(State):
    publisher: Publisher
    subscriber: Subscriber
    request_serializer: Schema
    authenticated: State

    def register(self) -> None:
        raise AlreadyRegisteredDeviceException()

    def authenticate(self) -> None:
        device = self.get_device()
        authentication_request = AuthenticationRequestDTO(device.device_id, device.token)
        self.publisher.content = str(self.request_serializer.dumps(authentication_request))
        self.publisher.publish()
        try:
            self.subscriber.callback.device_id = device.device_id
            self.subscriber.subscribe()
            device.transition_to_state(self.authenticated)
        except AuthenticationErrorException:
            ...
        self.set_device(device)

    def update_schema(self) -> None:
        raise NotAuthenticatedException()

    def publish_data(self) -> None:
        raise NotAuthenticatedException()

    def __repr__(self) -> str:
        return "registered"


@dataclass
class UnregisteredState(State):
    publisher: Publisher
    register_serializer: Schema
    registered: State

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


@dataclass
class AuthenticatedState(State):
    publisher: Publisher
    subscriber: Subscriber
    request_serializer: Schema
    updated_schema_state: State

    def register(self) -> None:
        raise AlreadyRegisteredDeviceException()

    def authenticate(self) -> None:
        raise AlreadyAuthenticatedException()

    def update_schema(self) -> None:
        device = self.get_device()
        config_request = UpdateConfigRequest(id=device.device_id, config=device.config)
        self.publisher.content = str(self.request_serializer.dumps(config_request))
        self.publisher.publish()
        try:
            self.subscriber.callback.device_id = device.device_id
            self.subscriber.subscribe()
            config = self.subscriber.callback.config
            if config:
                device.config = config
            device.transition_to_state(self.updated_schema_state)
        except UpdateConfigurationException:
            ...
        self.set_device(device)

    def publish_data(self) -> None:
        raise NotReadyException()

    def __repr__(self) -> str:
        return "authenticated"


@dataclass
class UpdatedSchemaState(State):
    ready_state: State

    def register(self) -> None:
        raise AlreadyRegisteredDeviceException()

    def authenticate(self) -> None:
        raise AlreadyAuthenticatedException()

    def update_schema(self) -> None:
        raise AlreadyUpdatedSchema()

    def publish_data(self) -> None:
        device = self.get_device()
        device.transition_to_state(self.ready_state)
        if device.data:
            device.publish_data()
        self.set_device(device)

    def __repr__(self) -> str:
        return "updatedSchema"


@dataclass
class ReadyState(State):
    publisher: Publisher
    publisher_serializer: Schema

    def register(self) -> None:
        raise AlreadyReady()

    def authenticate(self) -> None:
        raise AlreadyReady()

    def update_schema(self) -> None:
        raise AlreadyReady()

    def publish_data(self) -> None:
        device = self.get_device()
        if device.data:
            data = PublishingData(id=device.device_id, data=device.data)
            serialized_data = str(self.publisher_serializer.dumps(data))
            self.publisher.content = serialized_data
            self.publisher.publish()
        self.set_device(device)

    def __repr__(self) -> str:
        return "readyToSendData"
