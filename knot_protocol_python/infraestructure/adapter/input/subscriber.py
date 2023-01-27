from json import loads
from abc import ABC, abstractmethod
from dataclasses import dataclass

from knot_protocol_python.infraestructure.adapter.input.connection import AMQPExchange, AMQPQueue
from knot_protocol_python.domain.boundary.input.subscriber import Subscriber
from knot_protocol_python.infraestructure.adapter.input.DTO.device_registration_response_DTO import DeviceRegistrationResponseDTO
from knot_protocol_python.infraestructure.adapter.input.DTO.device_auth_response_DTO import AuthDeviceResponseDTO
from knot_protocol_python.infraestructure.adapter.input.DTO.device_configuration_response_DTO import ConfigUpdateResponseSchema
from knot_protocol_python.domain.exceptions.device_exception import (
    AlreadyRegisteredDeviceException,
    AuthenticationErrorException,
    UpdateConfigurationException)
from knot_protocol_python.domain.DTO.device_configuration import Schema


class AMQPCallback(ABC):
    @abstractmethod
    def execute(self, channel, method, properties, body):
        ...


@dataclass
class RegisterCallback(AMQPCallback):
    token: str
    consumer_tag: str

    def execute(self, channel, method, properties, body):
        dict_body = loads(body.decode("utf-8"))
        response = DeviceRegistrationResponseDTO().load(dict_body)
        if response.error == "device already exists":
            raise AlreadyRegisteredDeviceException(response.error)
        self.token = response.token if response.error is None else None
        channel.basic_cancel(consumer_tag=self.consumer_tag)


@dataclass
class UpdateSchemaCallback(AMQPCallback):
    consumer_tag: str
    config: Schema

    def execute(self, channel, method, properties, body):
        dict_body = loads(body.decode("utf-8"))
        print(dict_body)
        response = ConfigUpdateResponseSchema().load(dict_body)
        if response.error is not None:
            raise UpdateConfigurationException(response.error)
        if response.changed:
            self.config = response.config
        channel.basic_cancel(consumer_tag=self.consumer_tag)


@dataclass
class AuthCallback(AMQPCallback):
    consumer_tag: str

    def execute(self, channel, method, properties, body):
        dict_body = loads(body.decode("utf-8"))
        response = AuthDeviceResponseDTO().load(dict_body)
        if response.error is not None:
            raise AuthenticationErrorException(response.error)
        channel.basic_cancel(consumer_tag=self.consumer_tag)


class AMQPSubscriber(Subscriber):
    def __init__(self, channel, consumer_tag: str, routing_key: str, queue_name: str) -> None:
        self.__exchange_name = "device"
        self.__exchange_type = "direct"
        self.__routing_key = routing_key
        self.__exchange = None
        self.__queue = None
        self.__queue_name = queue_name
        self.__channel = channel
        self.__consumer_tag = consumer_tag
        self.__configure_exchange(self.__channel)
        self.__configure_queue(self.__channel)

    def subscribe(self):
        self.__start()

    def unsubscribe(self):
        ...

    def __start(self):
        self.__channel.basic_consume(
            queue=self.__queue.name,
            auto_ack=True,
            on_message_callback=self.__callback.execute,
            consumer_tag=self.__consumer_tag)
        self.__channel.start_consuming()

    def __configure_exchange(self, channel):
        self.__exchange = AMQPExchange(
            exchange_name=self.__exchange_name,
            exchange_type=self.__exchange_type,
            channel=channel)
        self.__exchange.declare()

    def __configure_queue(self, channel):
        self.__queue = AMQPQueue(channel=channel, name=self.__queue_name)
        self.__queue.declare()
        self.__queue.bind(exchange_name=self.__exchange.name, routing_key=self.__routing_key)

    @property
    def callback(self):
        return self.__callback

    @callback.setter
    def callback(self, callback):
        self.__callback = callback
