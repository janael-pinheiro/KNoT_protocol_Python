from pika import BasicProperties, URLParameters
from pika.exchange_type import ExchangeType
from os import environ

from knot_protocol.infrastructure.adapter.input.subscriber import (
    AMQPSubscriber, AuthCallback, RegisterCallback, UpdateSchemaCallback, UnregisterCallback)
from knot_protocol.infrastructure.adapter.output.publisher import \
    AMQPPublisher
from knot_protocol.infrastructure.utils.knot_amqp_options import (
    KNoTExchange, KNoTRoutingKey)
from knot_protocol.infrastructure.adapter.input.amqp_connection import AMQPConnection, AMQPChannel, AMQPExchange

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