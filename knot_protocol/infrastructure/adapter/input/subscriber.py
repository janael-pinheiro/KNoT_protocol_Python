from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import environ
from logging import Logger

from pika import URLParameters
from pika.exceptions import ConnectionClosedByBroker
from pika.channel import Channel
from tenacity import retry
from tenacity.retry import retry_if_exception_type
from tenacity.wait import wait_exponential

from knot_protocol.domain.boundary.input.subscriber import Subscriber
from knot_protocol.domain.boundary.output.DTO.schema import SchemaDTO
from knot_protocol.domain.exceptions.device_exception import (
    AlreadyRegisteredDeviceException,
    AuthenticationErrorException,
    UpdateConfigurationException,
    DifferentDeviceIdentifierException,
    UnregisteredException,
    DeviceNotFoundException,
    UnauthorizedException)
from knot_protocol.infrastructure.adapter.input.amqp_connection import (
    AMQPChannel, AMQPConnection, AMQPQueue)
from knot_protocol.infrastructure.adapter.input.DTO.device_auth_response_DTO import \
    AuthDeviceResponseDTO
from knot_protocol.infrastructure.adapter.input.DTO.device_configuration_response_DTO import \
    ConfigUpdateResponseSchema
from knot_protocol.infrastructure.adapter.input.DTO.device_registration_response_DTO import \
    DeviceRegistrationResponseDTO
from knot_protocol.infrastructure.adapter.input.DTO.device_unregistration_response import DeviceUnregistrationResponseDTO
from knot_protocol.infrastructure.utils.error_messages import KNoTErrorMessage
from knot_protocol.infrastructure.utils.knot_amqp_options import KNoTExchange
from knot_protocol.infrastructure.utils.utils import json_parser
from knot_protocol.infrastructure.utils.logger import logger_factory

logger = logger_factory()

FIVE_MINUTES_IN_SECONDS = 300


def delete_queue(channel: Channel, queue_name: str):
    channel.queue_delete(queue=queue_name, if_unused=False, if_empty=False)


def message_handler(func):
    CHANNEL_INDEX: int = 1
    METHOD_INDEX: int = 2
    def wrapper(*args):
        channel = args[CHANNEL_INDEX]
        method = args[METHOD_INDEX]
        if channel.is_open:
            try:
                func(*args)
            except (
                UnauthorizedException,
                AlreadyRegisteredDeviceException,
                DeviceNotFoundException,
                AuthenticationErrorException) as exception:
                channel.basic_ack(delivery_tag=method.delivery_tag, multiple=False)
                channel.cancel()
                logger.error(f"Error: {exception}")
            except DifferentDeviceIdentifierException:
                channel.basic_nack(delivery_tag=method.delivery_tag, multiple=False, requeue=False)
            except Exception:
                channel.basic_nack(delivery_tag=method.delivery_tag, multiple=False, requeue=True)
            else:
                channel.basic_ack(delivery_tag=method.delivery_tag, multiple=False)
                channel.cancel()
    return wrapper


class AMQPCallback(ABC):
    @abstractmethod
    def execute(self, channel, method, properties, body, queue_name):
        ...


@dataclass
class RegisterCallback(AMQPCallback):
    token: str
    consumer_tag: str = ""
    device_id: str = ""

    @message_handler
    def execute(self, channel, method, properties, body, queue_name):
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
    def execute(self, channel, method, properties, body, queue_name):
        dict_body = json_parser(body)
        response = DeviceUnregistrationResponseDTO().load(dict_body)
        if response.id != self.device_id:
            raise DifferentDeviceIdentifierException()
        if response.error == KNoTErrorMessage.device_not_found.value:
            raise DeviceNotFoundException(response.error)
        if response.error is not None:
            raise UnregisteredException(response.error)


@dataclass
class AuthCallback(AMQPCallback):
    consumer_tag: str = ""
    device_id: str = ""

    @message_handler
    def execute(self, channel, method, properties, body, queue_name):
        dict_body = json_parser(body)
        response = AuthDeviceResponseDTO().load(dict_body)
        if response.id != self.device_id:
            raise DifferentDeviceIdentifierException()
        if response.error == KNoTErrorMessage.unauthorized_device.value:
            raise UnauthorizedException(response.error)
        if response.error is not None:
            raise AuthenticationErrorException(response.error)


@dataclass
class UpdateSchemaCallback(AMQPCallback):
    consumer_tag: str = ""
    config: SchemaDTO = None
    device_id: str = ""

    @message_handler
    def execute(self, channel, method, properties, body, queue_name):
        dict_body = json_parser(body)
        response = ConfigUpdateResponseSchema().load(dict_body)
        if response.id != self.device_id:
            raise DifferentDeviceIdentifierException()
        if response.error == KNoTErrorMessage.device_not_found.value:
            raise DeviceNotFoundException(response.error)
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
    routing_key: str
    timeout: int = environ.get("CONSUMER_TIMEOUT", FIVE_MINUTES_IN_SECONDS)

    def __enter__(self) -> None:
        self.__queue_setup()

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        self.__queue_teardown()

    def __queue_setup(self):
        queue = AMQPQueue(channel=self.channel, name=self.queue_name)
        queue.declare()
        queue.bind(
            exchange_name=KNoTExchange.device_exchange.value,
            routing_key=self.routing_key)
    
    def __queue_teardown(self):
        self.channel.queue_delete(queue=self.queue_name, if_unused=False, if_empty=False)

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
        self.channel.cancel()

    def __start(self):
        for method, properties, body in self.channel.consume(
            queue=self.queue_name,
            inactivity_timeout=self.timeout):
            if self.__is_message_timeout(method, properties, body):
                logger.error("Timeout!")
                break
            self.callback.execute(self.channel, method, properties, body, self.queue_name)

    def __is_message_timeout(self, method, properties, body):
        return method is None and properties is None and body is None
