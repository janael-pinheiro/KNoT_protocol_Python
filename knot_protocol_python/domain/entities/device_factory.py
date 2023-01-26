from pika import URLParameters, BasicProperties

from knot_protocol_python.domain.entities.device_entity import DeviceEntity
from knot_protocol_python.infraestructure.adapter.input.subscriber import RegisterSubscriber, AuthSubscriber, UpdateConfigSubscriber
from knot_protocol_python.infraestructure.adapter.output.publisher import (
    RegisterPublisher,
    AuthPublisher,
    UpdateConfigPublisher,
    DataPublisher,
    AMQPPublisher)

from knot_protocol_python.domain.usecase.states import (
    DisconnectedState,
    RegisteredState,
    UnregisteredState,
    AuthenticatedState,
    UpdatedSchemaState,
    ReadyState)

from knot_protocol_python.infraestructure.adapter.output.DTO.device_registration_request_DTO import DeviceRegistrationRequestDTO
from knot_protocol_python.infraestructure.adapter.output.DTO.device_auth_request_DTO import DeviceAuthRequestDTO
from knot_protocol_python.infraestructure.adapter.output.DTO.update_config_schema import UpdateConfigRequestSchema
from knot_protocol_python.domain.DTO.event import Event
from knot_protocol_python.domain.DTO.schema import Schema
from knot_protocol_python.domain.DTO.device_configuration import SchemaDTO
from knot_protocol_python.domain.DTO.data_point import DataPointDTO
from knot_protocol_python.infraestructure.adapter.output.DTO.device_schema import DataPointsSchema


class DeviceFactory():

    @classmethod
    def create(cls, parameters: URLParameters, channel, knot_token: str) -> DeviceEntity:
        register_subscriber = RegisterSubscriber(parameters=parameters)
        auth_subscriber = AuthSubscriber(parameters=parameters)
        update_config_subscriber = UpdateConfigSubscriber(parameters=parameters)
        amqp_properties = BasicProperties(headers={"Authorization": f"{knot_token}"})
        register_publisher = AMQPPublisher(
            channel=channel,
            properties=amqp_properties,
            exchange_name="device",
            routing_key="device.register",
            )

        auth_properties = BasicProperties(
            headers={"Authorization": f"{knot_token}"},
            reply_to="device-auth-rpc",
            correlation_id="auth_correlation_id")
        auth_publisher = AMQPPublisher(
            channel=channel,
            exchange_name="device",
            routing_key="device.auth",
            properties=auth_properties)

        update_config_publisher = AMQPPublisher(
            channel=channel,
            exchange_name="device",
            routing_key="device.config.sent",
            properties=amqp_properties
        )

        data_publisher = AMQPPublisher(
            channel=channel,
            exchange_name="data.sent",
            routing_key="",
            properties=amqp_properties
        )

        ready_state = ReadyState(
            publisher=data_publisher,
            publisher_serializer=DataPointsSchema())

        updated_schema_state = UpdatedSchemaState(ready_state=ready_state)
        authenticated_state = AuthenticatedState(
            publisher=update_config_publisher,
            subscriber=update_config_subscriber,
            request_serializer=UpdateConfigRequestSchema(),
            updated_schema_state=updated_schema_state)

        registered_state = RegisteredState(
            publisher=auth_publisher,
            subscriber=auth_subscriber,
            request_serializer=DeviceAuthRequestDTO(),
            authenticated=authenticated_state)

        disconnected_state = DisconnectedState(
            authenticate_publisher=auth_publisher,
            authenticate_subscriber=auth_subscriber,
            register_publisher=register_publisher,
            register_subscriber=register_subscriber,
            registered_state=registered_state,
            authenticated=authenticated_state,
            register_serializer=DeviceRegistrationRequestDTO(),
            authenticate_serializer=DeviceAuthRequestDTO())
        schema = Schema(type_id=65521, unit=0, value_type=2, name="temperature")
        event = Event(change=True, time_seconds=5, lower_threshold=4, upper_threshold=10)
        configuration = SchemaDTO(event=event, schema=schema, sensor_id=1)
        data_point = DataPointDTO(sensor_id=1, value=42.2, timestamp="2023-01-21 12:15:00")
        device = DeviceEntity(
            device_id="",
            name="knot device",
            config=[configuration],
            state=disconnected_state,
            data_points=[data_point],
            error="",
            token="")
        device.transition_to_state(disconnected_state)
        return device
