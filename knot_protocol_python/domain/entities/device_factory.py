from pika import BasicProperties

from knot_protocol_python.domain.entities.device_entity import DeviceEntity
from knot_protocol_python.infraestructure.adapter.input.subscriber import (
    AMQPSubscriber,
    RegisterCallback,
    UpdateSchemaCallback,
    AuthCallback)
from knot_protocol_python.infraestructure.adapter.output.publisher import AMQPPublisher

from knot_protocol_python.domain.usecase.states import (
    DisconnectedState,
    RegisteredState,
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
from knot_protocol_python.infraestructure.adapter.input.connection import AMQPQueue
from knot_protocol_python.infraestructure.utils.knot_amqp_options import KNoTExchange, KNoTRoutingKey
from knot_protocol_python.infraestructure.utils.utils import logger_factory


class DeviceFactory():

    @classmethod
    def create(cls, subscriber_channel, publisher_channel, knot_token: str) -> DeviceEntity:
        logger = logger_factory()
        register_callback = RegisterCallback(consumer_tag="device_register", token="")
        register_queue = AMQPQueue(channel=subscriber_channel, name="device_registered")
        register_queue.declare()
        register_queue.bind(exchange_name=KNoTExchange.device_exchange.value, routing_key=KNoTRoutingKey.registered_device.value)
        register_subscriber = AMQPSubscriber(
            channel=subscriber_channel,
            consumer_tag="device_register",
            queue_name="device_registered",
            logger=logger,
            callback=register_callback)

        auth_queue = AMQPQueue(channel=subscriber_channel, name="device_auth_queue")
        auth_queue.declare()
        auth_queue.bind(exchange_name=KNoTExchange.device_exchange.value, routing_key="device-auth-rpc")
        auth_callback = AuthCallback(consumer_tag="device_auth")
        auth_subscriber = AMQPSubscriber(
            channel=subscriber_channel,
            consumer_tag="device_auth",
            queue_name="device_auth_queue",
            logger=logger,
            callback=auth_callback)

        update_schema_queue = AMQPQueue(channel=subscriber_channel, name="device_schema")
        update_schema_queue.declare()
        update_schema_queue.bind(exchange_name=KNoTExchange.device_exchange.value, routing_key=KNoTRoutingKey.updated_schema.value)
        update_schema_callback = UpdateSchemaCallback(consumer_tag="device_config_update", config=None)
        update_config_subscriber = AMQPSubscriber(
            channel=subscriber_channel,
            consumer_tag="device_config_update",
            queue_name="device_schema",
            logger=logger,
            callback=update_schema_callback)

        amqp_properties = BasicProperties(headers={"Authorization": f"{knot_token}"})
        register_publisher = AMQPPublisher(
            channel=publisher_channel,
            properties=amqp_properties,
            exchange_name="device",
            routing_key="device.register",
            logger=logger
            )

        auth_properties = BasicProperties(
            headers={"Authorization": f"{knot_token}"},
            reply_to="device-auth-rpc",
            correlation_id="auth_correlation_id")
        auth_publisher = AMQPPublisher(
            channel=publisher_channel,
            exchange_name="device",
            routing_key="device.auth",
            properties=auth_properties,
            logger=logger)

        update_config_publisher = AMQPPublisher(
            channel=publisher_channel,
            exchange_name="device",
            routing_key="device.config.sent",
            properties=amqp_properties,
            logger=logger
        )

        data_publisher = AMQPPublisher(
            channel=publisher_channel,
            exchange_name=KNoTExchange.data_sent_exchange.value,
            routing_key="",
            properties=amqp_properties,
            logger=logger
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
