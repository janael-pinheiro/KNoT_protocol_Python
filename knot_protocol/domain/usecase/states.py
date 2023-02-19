from dataclasses import dataclass
from typing import Any
from marshmallow import Schema

from knot_protocol.domain.boundary.input.subscriber import Subscriber
from knot_protocol.domain.boundary.output.DTO.authentication_request_dto import \
    AuthenticationRequestDTO
from knot_protocol.domain.boundary.output.DTO.publishing_data_dto import \
    PublishingData
from knot_protocol.domain.boundary.output.DTO.registration_request_dto import \
    RegistrationRequest
from knot_protocol.domain.boundary.output.DTO.unregistration_request import UnregistrationRequest
from knot_protocol.domain.boundary.output.DTO.update_config_request import \
    UpdateConfigRequest
from knot_protocol.domain.boundary.output.publisher import Publisher
from knot_protocol.domain.exceptions.device_exception import (
    AlreadyAuthenticatedException,
    AlreadyReady,
    AlreadyRegisteredDeviceException,
    AlreadyUpdatedSchema,
    NotAuthenticatedException,
    NotReadyException,
    NotRegisteredException,
    AlreadyUnregisteredDeviceException)
from knot_protocol.domain.usecase.state import State


@dataclass
class CommonStateOperation:
    device: Any
    unregister_subscriber: Subscriber
    unregister_publisher: Publisher
    unregister_serializer: Schema
    unregister_state: State
    register_subscriber: Subscriber
    register_publisher: Publisher
    register_serializer: Schema
    register_state: State

    def unregister(self):
        unregistration_request = UnregistrationRequest(
            id=self.device.device_id,
            name=self.device.name)
        self.unregister_publisher.content =\
            str(self.unregister_serializer.dumps(unregistration_request))
        with self.unregister_subscriber:
            self.unregister_publisher.publish()
            self.unregister_subscriber.callback.device_id = self.device.device_id
            self.unregister_subscriber.subscribe()
        self.device.token = None
        self.device.transition_to_state(self.unregister_state)
    
    def register(self):
        if not self.device.is_valid_device_id():
            self.device.device_id = self.device.create_id()
        if not self.device.is_valid_token():
            registration_request = RegistrationRequest(self.device.device_id, self.device.name)
            self.register_publisher.content = str(self.register_serializer.dumps(registration_request))
            with self.register_subscriber:
                self.register_publisher.publish()
                self.register_subscriber.callback.device_id = self.device.device_id
                self.register_subscriber.subscribe()
                token = self.register_subscriber.callback.token
            if token:
                self.device.token = token
                self.device.transition_to_state(self.register_state)
            return
        self.device.transition_to_state(self.register_state)


@dataclass
class DisconnectedState(State):
    authenticate_subscriber: Subscriber
    authenticate_publisher: Publisher
    registered_state: State
    authenticated: State
    authenticate_serializer: Schema
    common_operation: CommonStateOperation

    def register(self) -> None:
        self.common_operation.device = self.device
        self.common_operation.register_state = self.registered_state
        self.common_operation.register()

    def unregister(self) -> None:
        self.common_operation.device = self.device
        self.common_operation.unregister()

    def authenticate(self) -> None:
        device = self.get_device()
        if not device.is_valid_token():
            return
        if not device.is_valid_device_id():
            return
        authentication_request = AuthenticationRequestDTO(device.device_id, device.token)
        self.authenticate_publisher.content = str(self.authenticate_serializer.dumps(authentication_request))
        with self.authenticate_subscriber:
            self.authenticate_publisher.publish()
            self.authenticate_subscriber.callback.device_id = device.device_id
            self.authenticate_subscriber.subscribe()
        device.transition_to_state(self.authenticated)
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
    common_operation: CommonStateOperation

    def register(self) -> None:
        raise AlreadyRegisteredDeviceException()

    def unregister(self) -> None:
        self.common_operation.device = self.device
        self.common_operation.unregister()

    def authenticate(self) -> None:
        device = self.get_device()
        authentication_request = AuthenticationRequestDTO(device.device_id, device.token)
        self.publisher.content = str(self.request_serializer.dumps(authentication_request))
        with self.subscriber:
            self.publisher.publish()
            self.subscriber.callback.device_id = device.device_id
            self.subscriber.subscribe()
        device.transition_to_state(self.authenticated)
        self.set_device(device)

    def update_schema(self) -> None:
        raise NotAuthenticatedException()

    def publish_data(self) -> None:
        raise NotAuthenticatedException()

    def __repr__(self) -> str:
        return "registered"


@dataclass
class UnregisteredState(State):
    common_operation: CommonStateOperation

    def register(self) -> None:
        self.common_operation.device = self.device
        self.common_operation.register()

    def unregister(self) -> None:
        raise AlreadyUnregisteredDeviceException()

    def authenticate(self) -> None:
        raise NotRegisteredException()

    def update_schema(self) -> None:
        raise NotRegisteredException()

    def publish_data(self) -> None:
        raise NotRegisteredException()

    def __repr__(self) -> str:
        return "unregistered"


@dataclass
class AuthenticatedState(State):
    publisher: Publisher
    subscriber: Subscriber
    request_serializer: Schema
    updated_schema_state: State
    common_operation: CommonStateOperation

    def register(self) -> None:
        raise AlreadyRegisteredDeviceException()

    def unregister(self) -> None:
        self.common_operation.device = self.device
        self.common_operation.unregister()

    def authenticate(self) -> None:
        raise AlreadyAuthenticatedException()

    def update_schema(self) -> None:
        device = self.get_device()
        config_request = UpdateConfigRequest(id=device.device_id, config=device.config)
        self.publisher.content = str(self.request_serializer.dumps(config_request))
        with self.subscriber:
            self.publisher.publish()
            self.subscriber.callback.device_id = device.device_id
            self.subscriber.subscribe()
            config = self.subscriber.callback.config
        if config:
            device.config = config
        device.transition_to_state(self.updated_schema_state)
        self.set_device(device)

    def publish_data(self) -> None:
        raise NotReadyException()

    def __repr__(self) -> str:
        return "authenticated"


@dataclass
class UpdatedSchemaState(State):
    ready_state: State
    common_operation: CommonStateOperation

    def register(self) -> None:
        raise AlreadyRegisteredDeviceException()

    def unregister(self) -> None:
        self.common_operation.device = self.device
        self.common_operation.unregister()

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
    common_operation: CommonStateOperation

    def register(self) -> None:
        raise AlreadyReady()

    def unregister(self) -> None:
        self.common_operation.device = self.device
        self.common_operation.unregister()

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
