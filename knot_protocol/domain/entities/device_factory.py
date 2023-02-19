from os import environ
from typing import List

from pika import BasicProperties, URLParameters
from pika.exchange_type import ExchangeType

from knot_protocol.domain.DTO.device_configuration import ConfigurationDTO
from knot_protocol.domain.entities.device_entity import DeviceEntity
from knot_protocol.domain.usecase.states import (
    AuthenticatedState,
    DisconnectedState,
    ReadyState,
    RegisteredState,
    UnregisteredState,
    UpdatedSchemaState,
    CommonStateOperation)
from knot_protocol.infraestructure.adapter.input.connection import (
    AMQPChannel, AMQPConnection, AMQPExchange, AMQPQueue)
from knot_protocol.infraestructure.adapter.input.subscriber import (
    AMQPSubscriber, AuthCallback, RegisterCallback, UpdateSchemaCallback, UnregisterCallback)
from knot_protocol.infraestructure.adapter.output.DTO.device_auth_request_DTO import \
    DeviceAuthRequestDTO
from knot_protocol.infraestructure.adapter.output.DTO.device_registration_request_DTO import \
    DeviceRegistrationRequestDTO
from knot_protocol.infraestructure.adapter.output.DTO.device_unregistration_request_dto import DeviceUnregistrationRequestDTO
from knot_protocol.infraestructure.adapter.output.DTO.device_schema import \
    DataPointsSchema
from knot_protocol.infraestructure.adapter.output.DTO.update_config_schema import \
    UpdateConfigRequestSchema
from knot_protocol.infraestructure.adapter.output.publisher import \
    AMQPPublisher
from knot_protocol.infraestructure.adapter.output.repositories.device_repository import \
    DeviceRepository
from knot_protocol.infraestructure.utils.knot_amqp_options import (
    KNoTExchange, KNoTRoutingKey)
from knot_protocol.infraestructure.utils.logger import logger_factory


def amqp_setup_generator():
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
    yield subscriber_channel, publisher_channel
    subscriber_channel.close()
    publisher_channel.close()
    subscriber_connection.close()
    publisher_connection.close()


def amqp_data_management_setup(logger, knot_token, device_id):
    amqp_generator = amqp_setup_generator()
    subscriber_channel, publisher_channel = next(amqp_generator)
    register_callback = RegisterCallback(token="")

    register_queue_name = f"device_registered_{device_id}"
    register_subscriber = AMQPSubscriber(
        channel=subscriber_channel,
        queue_name=register_queue_name,
        logger=logger,
        callback=register_callback,
        routing_key=KNoTRoutingKey.registered_device.value)

    unregister_queue_name = f"device_unregistered_{device_id}"
    unregister_callback = UnregisterCallback()
    unregister_subscriber = AMQPSubscriber(
        channel=subscriber_channel,
        callback=unregister_callback,
        logger=logger,
        queue_name=unregister_queue_name,
        routing_key=KNoTRoutingKey.unregistered_device.value
    )

    auth_queue_name = f"device_auth_queue_{device_id}"
    auth_callback = AuthCallback()
    auth_subscriber = AMQPSubscriber(
        channel=subscriber_channel,
        queue_name=auth_queue_name,
        logger=logger,
        callback=auth_callback,
        routing_key="device-auth-rpc")

    update_schema_queue_name = f"device_schema_{device_id}"
    update_schema_callback = UpdateSchemaCallback(config=None)
    update_config_subscriber = AMQPSubscriber(
        channel=subscriber_channel,
        queue_name=update_schema_queue_name,
        logger=logger,
        callback=update_schema_callback,
        routing_key=KNoTRoutingKey.updated_schema.value)

    persistent_message_code = 2
    amqp_properties = BasicProperties(
        headers={"Authorization": f"{knot_token}"},
        delivery_mode=persistent_message_code)
    register_publisher = AMQPPublisher(
        channel=publisher_channel,
        properties=amqp_properties,
        exchange_name="device",
        routing_key="device.register",
        logger=logger
        )

    unregister_publisher = AMQPPublisher(
        channel=publisher_channel,
        properties=amqp_properties,
        exchange_name="device",
        routing_key="device.unregister",
        logger=logger
    )

    auth_properties = BasicProperties(
        headers={"Authorization": f"{knot_token}"},
        reply_to="device-auth-rpc",
        correlation_id="auth_correlation_id",
        delivery_mode=persistent_message_code)
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
        data_publisher,
        unregister_subscriber,
        unregister_publisher,
        amqp_generator)


def state_machine_assembler(device_id: str):
    logger = logger_factory()
    knot_token = environ.get("KNOT_TOKEN")
    (
    register_subscriber,
    auth_subscriber,
    update_config_subscriber,
    register_publisher,
    auth_publisher,
    update_config_publisher,
    data_publisher,
    unregister_subscriber,
    unregister_publisher,
    amqp_generator) = amqp_data_management_setup(logger=logger, knot_token=knot_token, device_id=device_id)

    common_operation = CommonStateOperation(
        unregister_subscriber=unregister_subscriber,
        unregister_publisher=unregister_publisher,
        device=None,
        unregister_serializer=DeviceUnregistrationRequestDTO(),
        unregister_state=None,
        register_publisher=register_publisher,
        register_subscriber=register_subscriber,
        register_serializer=DeviceRegistrationRequestDTO(),
        register_state=None)
    
    ready_state = ReadyState(
        publisher=data_publisher,
        publisher_serializer=DataPointsSchema(),
        common_operation=common_operation)

    updated_schema_state = UpdatedSchemaState(ready_state=ready_state, common_operation=common_operation)
    authenticated_state = AuthenticatedState(
        publisher=update_config_publisher,
        subscriber=update_config_subscriber,
        request_serializer=UpdateConfigRequestSchema(),
        updated_schema_state=updated_schema_state,
        common_operation=common_operation)

    registered_state = RegisteredState(
        publisher=auth_publisher,
        subscriber=auth_subscriber,
        request_serializer=DeviceAuthRequestDTO(),
        authenticated=authenticated_state,
        common_operation=common_operation)

    unregistered_state = UnregisteredState(common_operation=common_operation)

    common_operation.unregister_state = unregistered_state

    disconnected_state = DisconnectedState(
        authenticate_publisher=auth_publisher,
        authenticate_subscriber=auth_subscriber,
        registered_state=registered_state,
        authenticated=authenticated_state,
        authenticate_serializer=DeviceAuthRequestDTO(),
        common_operation=common_operation)

    return disconnected_state, amqp_generator


class DeviceFactory():

    @classmethod
    def __validate_sensor_uniqueness(cls, schema: List[ConfigurationDTO]):
        number_sensors: int = len(schema)
        unique_sensors = set(schema)
        number_unique_sensores = len(unique_sensors)
        if number_sensors != number_unique_sensores:
            raise Exception("Sensors with duplicate identifiers.")

    @classmethod
    def create(cls, name: str, schema: List[ConfigurationDTO]) -> DeviceEntity:
        cls.__validate_sensor_uniqueness(schema=schema)
        device_id = DeviceEntity.create_id()
        disconnected_state, amqp_generator = state_machine_assembler(device_id=device_id)

        device = DeviceEntity(
            device_id=device_id,
            name=name,
            config=schema,
            state=disconnected_state,
            data=[None],
            error="",
            token="",
            amqp_generator=amqp_generator)
        device.transition_to_state(disconnected_state)
        return device

    @classmethod
    def load_existing_device(cls, device_repository: DeviceRepository) -> DeviceEntity:
        device = device_repository.load()
        disconnected_state, amqp_generator = state_machine_assembler(device_id=device.device_id)
        device.amqp_generator = amqp_generator
        device.transition_to_state(disconnected_state)
        return device
