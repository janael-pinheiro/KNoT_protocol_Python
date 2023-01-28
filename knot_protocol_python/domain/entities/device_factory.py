from os import environ
from typing import List

from pika import BasicProperties, URLParameters
from pika.exchange_type import ExchangeType

from knot_protocol_python.domain.DTO.schema import Schema
from knot_protocol_python.domain.entities.device_entity import DeviceEntity
from knot_protocol_python.domain.usecase.states import (AuthenticatedState,
                                                        DisconnectedState,
                                                        ReadyState,
                                                        RegisteredState,
                                                        UpdatedSchemaState)
from knot_protocol_python.infraestructure.adapter.input.connection import (
    AMQPChannel, AMQPConnection, AMQPExchange, AMQPQueue)
from knot_protocol_python.infraestructure.adapter.input.subscriber import (
    AMQPSubscriber, AuthCallback, RegisterCallback, UpdateSchemaCallback)
from knot_protocol_python.infraestructure.adapter.output.DTO.device_auth_request_DTO import \
    DeviceAuthRequestDTO
from knot_protocol_python.infraestructure.adapter.output.DTO.device_registration_request_DTO import \
    DeviceRegistrationRequestDTO
from knot_protocol_python.infraestructure.adapter.output.DTO.device_schema import \
    DataPointsSchema
from knot_protocol_python.infraestructure.adapter.output.DTO.update_config_schema import \
    UpdateConfigRequestSchema
from knot_protocol_python.infraestructure.adapter.output.publisher import \
    AMQPPublisher
from knot_protocol_python.infraestructure.adapter.output.repositories.device_repository import \
    DeviceRepository
from knot_protocol_python.infraestructure.utils.knot_amqp_options import (
    KNoTExchange, KNoTRoutingKey)
from knot_protocol_python.infraestructure.utils.utils import (
    generate_consumer_tag, logger_factory)


def amqp_setup():
    parameters = URLParameters(environ.get("AMQP_URL"))
    subscriber_connection = AMQPConnection(parameters=parameters).create()
    publisher_connection = AMQPConnection(parameters=parameters).create()
    subscriber_channel = AMQPChannel(connection=subscriber_connection).create()
    BUFFER_LENGTH: int = 1
    subscriber_channel.basic_qos(prefetch_count=BUFFER_LENGTH)
    publisher_channel = AMQPChannel(connection=publisher_connection).create()
    publisher_channel.confirm_delivery()
    AMQPExchange(
        channel=subscriber_channel,
        exchange_name=KNoTExchange.device_exchange.value,
        exchange_type=ExchangeType.direct).declare()
    AMQPExchange(
        channel=subscriber_channel,
        exchange_name=KNoTExchange.data_sent_exchange.value,
        exchange_type=ExchangeType.fanout
    ).declare()
    return subscriber_channel, publisher_channel


def amqp_data_management_setup(logger, knot_token):
    subscriber_channel, publisher_channel = amqp_setup()
    register_consumer_tag = generate_consumer_tag()
    register_callback = RegisterCallback(consumer_tag=register_consumer_tag, token="")
    
    register_queue = AMQPQueue(channel=subscriber_channel, name="device_registered")
    register_queue.declare()
    register_queue.bind(exchange_name=KNoTExchange.device_exchange.value, routing_key=KNoTRoutingKey.registered_device.value)
    register_subscriber = AMQPSubscriber(
        channel=subscriber_channel,
        consumer_tag=register_consumer_tag,
        queue_name="device_registered",
        logger=logger,
        callback=register_callback)

    auth_queue = AMQPQueue(channel=subscriber_channel, name="device_auth_queue")
    auth_queue.declare()
    auth_queue.bind(exchange_name=KNoTExchange.device_exchange.value, routing_key="device-auth-rpc")
    auth_consumer_tag = generate_consumer_tag()
    auth_callback = AuthCallback(consumer_tag=auth_consumer_tag)
    auth_subscriber = AMQPSubscriber(
        channel=subscriber_channel,
        consumer_tag=auth_consumer_tag,
        queue_name="device_auth_queue",
        logger=logger,
        callback=auth_callback)

    update_schema_queue = AMQPQueue(channel=subscriber_channel, name="device_schema")
    update_schema_queue.declare()
    update_schema_queue.bind(exchange_name=KNoTExchange.device_exchange.value, routing_key=KNoTRoutingKey.updated_schema.value)
    schema_consumer_tag = generate_consumer_tag()
    update_schema_callback = UpdateSchemaCallback(consumer_tag=schema_consumer_tag, config=None)
    update_config_subscriber = AMQPSubscriber(
        channel=subscriber_channel,
        consumer_tag=schema_consumer_tag,
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

    return (
        register_subscriber,
        auth_subscriber,
        update_config_subscriber,
        register_publisher,
        auth_publisher,
        update_config_publisher,
        data_publisher)


def state_machine_assembler():
    logger = logger_factory()
    knot_token = environ.get("KNOT_TOKEN")
    (
    register_subscriber,
    auth_subscriber,
    update_config_subscriber,
    register_publisher,
    auth_publisher,
    update_config_publisher,
    data_publisher) = amqp_data_management_setup(logger=logger, knot_token=knot_token)

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
    
    return disconnected_state


class DeviceFactory():

    @classmethod
    def create(cls, name: str, schema: List[Schema]) -> DeviceEntity:
        disconnected_state = state_machine_assembler()

        device = DeviceEntity(
            device_id=DeviceEntity.create_id(),
            name=name,
            config=schema,
            state=disconnected_state,
            data=[None],
            error="",
            token="")
        device.transition_to_state(disconnected_state)
        return device

    @classmethod
    def load_existing_device(cls, device_repository: DeviceRepository) -> DeviceEntity:
        disconnected_state = state_machine_assembler()
        device = device_repository.load()
        device.transition_to_state(disconnected_state)
        return device
