from pika import URLParameters
from os import environ
from time import sleep
from random import uniform
from datetime import datetime
import yaml

from knot_protocol_python.infraestructure.adapter.input.connection import AMQPConnection, AMQPChannel
from knot_protocol_python.domain.usecase.states import (
    NewState,
    WaitRegistrationState,
    RegisteredState,
    UnregisteredState,
    WaitAuthenticateState,
    AuthenticatedState,
    UnauthenticatedState,
    WaitConfigState,
    ReadyState,
    PublishingState)
from knot_protocol_python.domain.entities.device_entity import DeviceEntity
from knot_protocol_python.infraestructure.adapter.input.subscriber import RegisterSubscriber, AuthSubscriber, UpdateConfigSubscriber
from knot_protocol_python.infraestructure.adapter.output.publisher import (
    RegisterPublisher,
    AuthPublisher,
    UpdateConfigPublisher,
    DataPublisher)
from knot_protocol_python.infraestructure.adapter.output.DTO.device_registration_request_DTO import DeviceRegistrationRequestDTO
from knot_protocol_python.infraestructure.adapter.output.DTO.device_auth_request_DTO import DeviceAuthRequestDTO
from knot_protocol_python.infraestructure.adapter.output.DTO.update_config_schema import UpdateConfigRequestSchema
from knot_protocol_python.domain.DTO.event import Event
from knot_protocol_python.domain.DTO.schema import Schema
from knot_protocol_python.domain.DTO.device_configuration import ConfigurationDTO
from knot_protocol_python.domain.DTO.data_point import DataPointDTO
from knot_protocol_python.infraestructure.adapter.output.DTO.device_schema import DataPointsSchema, DeviceSchema


if __name__ == "__main__":
    knot_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDU5Mjc3NzIsImp0aSI6Ijc5N2I4MmJlLWNiMzMtNGFhNi1iYTkwLWZkOTFjNTU3NmEwNCIsImlhdCI6MTY3NDM5MTc3MiwiaXNzIjoiYWpwQGtub3Qub3JnLmJyIiwidHlwZSI6Mn0.TUu_3OJADMblSKXDMUkJu7lzVmUMkzOiNAEfBuXIQVw"
    parameters = URLParameters(environ.get("AMQP_URL"))
    with AMQPConnection(parameters=parameters) as connection:
        with AMQPChannel(connection=connection) as channel:
            register_subscriber = RegisterSubscriber(parameters=parameters)
            auth_subscriber = AuthSubscriber(parameters=parameters)
            update_config_subscriber = UpdateConfigSubscriber(parameters=parameters)
            register_publisher = RegisterPublisher(channel=channel, knot_token=knot_token)
            auth_publisher = AuthPublisher(channel=channel, knot_token=knot_token)
            update_config_publisher = UpdateConfigPublisher(channel=channel, knot_token=knot_token)
            data_publisher = DataPublisher(channel=channel, knot_token=knot_token)
            ready_state = ReadyState(
                device=None,
                publisher=data_publisher,
                publisher_serializer=DataPointsSchema(),
                publishing_state=PublishingState())
            wait_config_state = WaitConfigState(
                device=None,
                subscriber=update_config_subscriber,
                ready_state=ready_state)
            authenticated_state = AuthenticatedState(
                device=None,
                publisher=update_config_publisher,
                request_serializer=UpdateConfigRequestSchema(),
                wait_configuration_state=wait_config_state)
            wait_authentication_state = WaitAuthenticateState(
                device=None,
                subscriber=auth_subscriber,
                authenticated_state=authenticated_state,
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
            schema = Schema(type_id=65521, unit=0, value_type=2, name="temperature")
            event = Event(change=True, time_seconds=5, lower_threshold=4, upper_threshold=10)
            configuration = ConfigurationDTO(event=event, schema=schema, sensor_id=1)
            data_point = DataPointDTO(sensorID=1, value=42.2, timestamp="2023-01-21 12:15:00")
            device = DeviceEntity(
                device_id="",
                name="knot device",
                config=[configuration],
                state=new_state,
                data_points=[data_point],
                error="",
                token="")
            
            print(type(device.state))
            print(device.token)
            device.handle_state()
            while not isinstance(device.state, ReadyState):
                if isinstance(device.state, WaitRegistrationState):
                    print("Waiting registration")
                    device.handle_state()
                if isinstance(device.state, RegisteredState):
                    print("Registered!!")
                    device.handle_state()
                if isinstance(device.state, WaitAuthenticateState):
                    print("Waiting authentication")
                    device.handle_state()
                if isinstance(device.state, AuthenticatedState):
                    print("Authenticated!")
                    device.handle_state()
                if isinstance(device.state, WaitConfigState):
                    print("Waiting configuration")
                    device.handle_state()
                sleep(1)
            serialized_device = DeviceSchema().dump(device)
            with open("device.yaml", "w", encoding="utf-8") as file_writer:
                yaml.dump(serialized_device, file_writer)

            print("Publishing data!")
            while True:
                data = DataPointDTO(sensorID=1, value=uniform(1.6, 89.2), timestamp=str(datetime.utcnow()))
                device.data_points = [data]
                device.handle_state()
                sleep(5)
