from pika import URLParameters
from os import environ
from time import sleep

from knot_protocol_python.infraestructure.adapter.input.connection import AMQPConnection, AMQPChannel
from knot_protocol_python.domain.usecase.states import (
    NewState,
    WaitRegistrationState,
    RegisteredState,
    UnregisteredState,
    WaitAuthenticateState,
    AuthenticatedState,
    UnauthenticatedState)
from knot_protocol_python.domain.entities.device_entity import DeviceEntity
from knot_protocol_python.infraestructure.adapter.input.subscriber import RegisterSubscriber, AuthSubscriber
from knot_protocol_python.infraestructure.adapter.output.publisher import RegisterPublisher, AuthPublisher
from knot_protocol_python.infraestructure.adapter.output.DTO.device_registration_request_DTO import DeviceRegistrationRequestDTO
from knot_protocol_python.infraestructure.adapter.output.DTO.device_auth_request_DTO import DeviceAuthRequestDTO


if __name__ == "__main__":
    knot_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDU5Mjc3NzIsImp0aSI6Ijc5N2I4MmJlLWNiMzMtNGFhNi1iYTkwLWZkOTFjNTU3NmEwNCIsImlhdCI6MTY3NDM5MTc3MiwiaXNzIjoiYWpwQGtub3Qub3JnLmJyIiwidHlwZSI6Mn0.TUu_3OJADMblSKXDMUkJu7lzVmUMkzOiNAEfBuXIQVw"
    parameters = URLParameters(environ.get("AMQP_URL"))
    connection = AMQPConnection(parameters=parameters).create()
    channel = AMQPChannel(connection=connection).create()
    register_subscriber = RegisterSubscriber(parameters=parameters)
    auth_subscriber = AuthSubscriber(parameters=parameters)
    register_publisher = RegisterPublisher(channel=channel, knot_token=knot_token)
    auth_publisher = AuthPublisher(channel=channel, knot_token=knot_token)
    wait_authentication_state = WaitAuthenticateState(
        device=None,
        subscriber=auth_subscriber,
        authenticated_state=AuthenticatedState(),
        unauthenticated_state=UnauthenticatedState())
    registered_state = RegisteredState(
        device=None,
        publisher=auth_publisher,
        request_serializer=DeviceAuthRequestDTO(),
        wait_authentication_state=wait_authentication_state)
    unregistered_state = UnregisteredState()
    wait_registration_state = WaitRegistrationState(
        device=None,
        subscriber=register_subscriber,
        registered_state=registered_state,
        unregistered_state=unregistered_state)
    new_state = NewState(
        device=None,
        wait_registration_state=wait_registration_state,
        publisher=register_publisher,
        request_serializer=DeviceRegistrationRequestDTO())
    device = DeviceEntity(
        device_id="",
        name="knot device",
        config=None,
        state=new_state,
        data_points=None,
        error="",
        token="")
    
    print(type(device.state))
    print(device.token)
    device.handle_state()
    while not isinstance(device.state, AuthenticatedState):
        if isinstance(device.state, RegisteredState):
            print("Registered!!")
            device.handle_state()
        sleep(1)
    print(type(device.state))
    print(device.token)
