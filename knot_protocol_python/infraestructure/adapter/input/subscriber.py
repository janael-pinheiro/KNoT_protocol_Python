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

from knot_protocol_python.domain.boundary.input.subscriber import Subscriber
from knot_protocol_python.domain.DTO.device_configuration import Schema
from knot_protocol_python.domain.exceptions.device_exception import (
    AlreadyRegisteredDeviceException, AuthenticationErrorException,
    UpdateConfigurationException)
from knot_protocol_python.infraestructure.adapter.input.connection import (
    AMQPChannel, AMQPConnection)
from knot_protocol_python.infraestructure.adapter.input.DTO.device_auth_response_DTO import \
    AuthDeviceResponseDTO
from knot_protocol_python.infraestructure.adapter.input.DTO.device_configuration_response_DTO import \
    ConfigUpdateResponseSchema
from knot_protocol_python.infraestructure.adapter.input.DTO.device_registration_response_DTO import \
    DeviceRegistrationResponseDTO
from knot_protocol_python.infraestructure.utils.error_messages import KNoTErrorMessage
from knot_protocol_python.infraestructure.utils.utils import json_parser


class AMQPCallback(ABC):
    @abstractmethod
    def execute(self, channel, method, properties, body, consumer_tag = ""):
        ...


def message_handler(func):
    CHANNEL_INDEX: int = 1
    METHOD_INDEX: int = 2
    def wrapper(*args, **kwargs):
        try:
            func(*args)
        except Exception as exception:
            args[CHANNEL_INDEX].basic_nack(
                delivery_tag=args[METHOD_INDEX].delivery_tag,
                multiple=False,
                requeue=True)
            raise exception
        else:
            args[CHANNEL_INDEX].basic_ack(delivery_tag=args[METHOD_INDEX].delivery_tag, multiple=False)
            args[CHANNEL_INDEX].basic_cancel(consumer_tag=kwargs["consumer_tag"])
    return wrapper


@dataclass
class RegisterCallback(AMQPCallback):
    token: str
    consumer_tag: str

    @message_handler
    def execute(self, channel, method, properties, body, consumer_tag = ""):
        dict_body = json_parser(body)
        response = DeviceRegistrationResponseDTO().load(dict_body)
        if response.error == KNoTErrorMessage.device_exists.value:
            raise AlreadyRegisteredDeviceException(response.error)
        self.token = response.token if response.error is None else None


@dataclass
class AuthCallback(AMQPCallback):
    consumer_tag: str

    @message_handler
    def execute(self, channel, method, properties, body, consumer_tag = ""):
        dict_body = json_parser(body)
        response = AuthDeviceResponseDTO().load(dict_body)
        if response.error is not None:
            raise AuthenticationErrorException(response.error)


@dataclass
class UpdateSchemaCallback(AMQPCallback):
    consumer_tag: str
    config: Schema = None

    @message_handler
    def execute(self, channel, method, properties, body, consumer_tag = ""):
        dict_body = json_parser(body)
        response = ConfigUpdateResponseSchema().load(dict_body)
        if response.error is not None:
            raise UpdateConfigurationException(response.error)
        if response.changed:
            self.config = response.config


@dataclass
class AMQPSubscriber(Subscriber):
    channel: Channel
    consumer_tag: str
    queue_name: str
    logger: Logger
    callback: AMQPCallback

    @retry(
        retry=retry_if_exception_type(ConnectionClosedByBroker),
        wait=wait_exponential(multiplier=1, min=4, max=10))
    def subscribe(self):
        if self.channel.connection.is_closed:
            self.logger.info("Subscriber connection closed! Reconnecting...")
            connection = AMQPConnection(URLParameters(environ.get("AMQP_URL"))).create()
            self.channel = AMQPChannel(connection=connection).create()
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
