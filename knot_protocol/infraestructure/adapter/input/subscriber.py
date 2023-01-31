from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import environ
from functools import partial
from logging import Logger

from pika import URLParameters
from pika.exceptions import ConnectionClosedByBroker
from pika.channel import Channel
from tenacity import retry
from tenacity.retry import retry_if_exception_type
from tenacity.wait import wait_exponential

from knot_protocol.domain.boundary.input.subscriber import Subscriber
from knot_protocol.domain.DTO.schema import SchemaDTO
from knot_protocol.domain.exceptions.device_exception import (
    AlreadyRegisteredDeviceException,
    AuthenticationErrorException,
    UpdateConfigurationException,
    DifferentDeviceIdentifierException,
    UnregisteredException)
from knot_protocol.infraestructure.adapter.input.connection import (
    AMQPChannel, AMQPConnection)
from knot_protocol.infraestructure.adapter.input.DTO.device_auth_response_DTO import \
    AuthDeviceResponseDTO
from knot_protocol.infraestructure.adapter.input.DTO.device_configuration_response_DTO import \
    ConfigUpdateResponseSchema
from knot_protocol.infraestructure.adapter.input.DTO.device_registration_response_DTO import \
    DeviceRegistrationResponseDTO
from knot_protocol.infraestructure.adapter.input.DTO.device_unregistration_response import DeviceUnregistrationResponseDTO
from knot_protocol.infraestructure.utils.error_messages import KNoTErrorMessage
from knot_protocol.infraestructure.utils.utils import json_parser, generate_consumer_tag


def message_handler(func):
    CHANNEL_INDEX: int = 1
    METHOD_INDEX: int = 2
    def wrapper(*args, **kwargs):
        channel = args[CHANNEL_INDEX]
        method = args[METHOD_INDEX]
        try:
            func(*args)
        except Exception as exception:
            if channel.is_open:
                channel.basic_nack(
                    delivery_tag=method.delivery_tag,
                    multiple=False,
                    requeue=True)
            raise exception
        else:
            if channel.is_open:
                channel.basic_ack(delivery_tag=method.delivery_tag, multiple=False)
                channel.basic_cancel(consumer_tag=kwargs["consumer_tag"])
    return wrapper


class AMQPCallback(ABC):
    @abstractmethod
    def execute(self, channel, method, properties, body, consumer_tag = ""):
        ...


@dataclass
class RegisterCallback(AMQPCallback):
    token: str
    consumer_tag: str = ""
    device_id: str = ""

    @message_handler
    def execute(self, channel, method, properties, body, consumer_tag = ""):
        dict_body = json_parser(body)
        response = DeviceRegistrationResponseDTO().load(dict_body)
        if response.id != self.device_id:
            raise DifferentDeviceIdentifierException()
        if response.error == KNoTErrorMessage.device_exists.value:
            raise AlreadyRegisteredDeviceException(response.error)
        self.token = response.token if response.error is None else None


@dataclass
class UnregisterCallback(AMQPCallback):
    consumer_tag: str = ""
    device_id: str = ""
    
    @message_handler
    def execute(self, channel, method, properties, body, consumer_tag=""):
        dict_body = json_parser(body)
        response = DeviceUnregistrationResponseDTO().load(dict_body)
        if response.id != self.device_id:
            raise DifferentDeviceIdentifierException()
        if response.error is not None:
            raise UnregisteredException(response.error)


@dataclass
class AuthCallback(AMQPCallback):
    consumer_tag: str = ""
    device_id: str = ""

    @message_handler
    def execute(self, channel, method, properties, body, consumer_tag = ""):
        dict_body = json_parser(body)
        response = AuthDeviceResponseDTO().load(dict_body)
        if response.id != self.device_id:
            raise DifferentDeviceIdentifierException()
        if response.error is not None:
            raise AuthenticationErrorException(response.error)


@dataclass
class UpdateSchemaCallback(AMQPCallback):
    consumer_tag: str = ""
    config: SchemaDTO = None
    device_id: str = ""

    @message_handler
    def execute(self, channel, method, properties, body, consumer_tag = ""):
        dict_body = json_parser(body)
        response = ConfigUpdateResponseSchema().load(dict_body)
        if response.id != self.device_id:
            raise DifferentDeviceIdentifierException()
        if response.error is not None:
            raise UpdateConfigurationException(response.error)
        if response.changed:
            self.config = response.config


@dataclass
class AMQPSubscriber(Subscriber):
    channel: Channel
    queue_name: str
    logger: Logger
    callback: AMQPCallback
    consumer_tag: str = ""

    @retry(
        retry=retry_if_exception_type(ConnectionClosedByBroker),
        wait=wait_exponential(multiplier=1, min=4, max=10))
    def subscribe(self):
        if self.channel.connection.is_closed:
            self.logger.info("Subscriber connection closed! Reconnecting...")
            connection = AMQPConnection(URLParameters(environ.get("AMQP_URL"))).create()
            self.channel = AMQPChannel(connection=connection).create()
        self.consumer_tag = generate_consumer_tag()
        self.callback.consumer_tag = self.consumer_tag
        self.__start()

    def unsubscribe(self):
        self.channel.basic_cancel(consumer_tag=self.consumer_tag)

    def __start(self):
        partial_callback = partial(self.callback.execute, consumer_tag=self.consumer_tag)
        self.channel.basic_consume(
            queue=self.queue_name,
            auto_ack=False,
            on_message_callback=partial_callback,
            consumer_tag=self.consumer_tag)
        self.channel.start_consuming()
