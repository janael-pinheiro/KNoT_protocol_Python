from pika import URLParameters
from json import loads

from knot_protocol_python.infraestructure.adapter.input.connection import AMQPConnection, AMQPChannel
from knot_protocol_python.infraestructure.adapter.input.connection import AMQPExchange, AMQPQueue
from knot_protocol_python.domain.boundary.input.subscriber import Subscriber
from knot_protocol_python.infraestructure.adapter.input.DTO.device_registration_response_DTO import DeviceRegistrationResponseDTO
from knot_protocol_python.infraestructure.adapter.input.DTO.device_auth_response_DTO import AuthDeviceResponseDTO
from knot_protocol_python.infraestructure.adapter.input.DTO.device_configuration_response_DTO import ConfigUpdateResponseSchema
from knot_protocol_python.domain.exceptions.device_exception import (
    AlreadyRegisteredDeviceExcepiton,
    AuthenticationErrorException,
    UpdateConfigurationException)


class RegisterSubscriber(Subscriber):

    def __init__(self, parameters: URLParameters) -> None:
        self.__exchange_name = "device"
        self.__exchange_type = "direct"
        self.__routing_key = "device.registered"
        self.__consumer_tag = "device_register"
        self.__parameters = parameters
        self.__exchange = None
        self.__queue = None
        self.__token = None
        with AMQPConnection(parameters=self.__parameters) as connection:
            with AMQPChannel(connection=connection) as channel:
                self.__configure_exchange(channel=channel)
                self.__configure_queue(channel=channel)

    def subscribe(self):
        self.__start()
        return self.__token

    def unsubscribe(self):
        ...

    def __start(self):
        with AMQPConnection(parameters=self.__parameters) as connection:
            with AMQPChannel(connection=connection) as channel:
                channel.basic_consume(
                    queue=self.__queue.name,
                    auto_ack=True,
                    on_message_callback=self.__callback,
                    consumer_tag=self.__consumer_tag)
                channel.start_consuming()

    def __configure_exchange(self, channel):
        self.__exchange = AMQPExchange(
            exchange_name=self.__exchange_name,
            exchange_type=self.__exchange_type,
            channel=channel)
        self.__exchange.declare()

    def __configure_queue(self, channel):
        self.__queue = AMQPQueue(channel=channel, name="device_registered")
        self.__queue.declare()
        self.__queue.bind(exchange_name=self.__exchange.name, routing_key=self.__routing_key)

    def __callback(self, channel, method, properties, body):
        dict_body = loads(body.decode("utf-8"))
        print(f"Registered response: {dict_body}")
        response = DeviceRegistrationResponseDTO().load(dict_body)
        if response.error == "device already exists":
            raise AlreadyRegisteredDeviceExcepiton(response.error)
        self.__token = response.token if response.error is None else None
        channel.basic_cancel(consumer_tag=self.__consumer_tag)


class AuthSubscriber(Subscriber):

    def __init__(self, parameters: URLParameters) -> None:
        self.__exchange_name = "device"
        self.__exchange_type = "direct"
        self.__routing_key = "device-auth-rpc"
        self.__consumer_tag = "device_auth"
        self.__parameters = parameters
        self.__exchange = None
        self.__queue = None
        with AMQPConnection(parameters=self.__parameters) as connection:
            with AMQPChannel(connection=connection) as channel:
                self.__configure_exchange(channel=channel)
                self.__configure_queue(channel=channel)

    def subscribe(self):
        self.__start()

    def unsubscribe(self):
        ...

    def __start(self):
        with AMQPConnection(parameters=self.__parameters) as connection:
            with AMQPChannel(connection=connection) as channel:
                channel.basic_consume(
                    queue=self.__queue.name,
                    auto_ack=True,
                    on_message_callback=self.__callback,
                    consumer_tag=self.__consumer_tag)
                channel.start_consuming()

    def __configure_exchange(self, channel):
        self.__exchange = AMQPExchange(
            exchange_name=self.__exchange_name,
            exchange_type=self.__exchange_type,
            channel=channel)
        self.__exchange.declare()

    def __configure_queue(self, channel):
        self.__queue = AMQPQueue(channel=channel, name="device_auth")
        self.__queue.declare()
        self.__queue.bind(exchange_name=self.__exchange.name, routing_key=self.__routing_key)

    def __callback(self, channel, method, properties, body):
        dict_body = loads(body.decode("utf-8"))
        print(f"Auth response: {dict_body}")
        response = AuthDeviceResponseDTO().load(dict_body)
        if response.error is not None:
            raise AuthenticationErrorException(response.error)
        channel.basic_cancel(consumer_tag=self.__consumer_tag)


class UpdateConfigSubscriber(Subscriber):

    def __init__(self, parameters: URLParameters) -> None:
        self.__exchange_name = "device"
        self.__exchange_type = "direct"
        self.__routing_key = "device.config.updated"
        self.__consumer_tag = "device_config_update"
        self.__parameters = parameters
        self.__exchange = None
        self.__queue = None
        self.__config = None
        with AMQPConnection(parameters=self.__parameters) as connection:
            with AMQPChannel(connection=connection) as channel:
                self.__configure_exchange(channel=channel)
                self.__configure_queue(channel=channel)

    def subscribe(self):
        self.__start()
        return self.__config

    def unsubscribe(self):
        ...

    def __start(self):
        with AMQPConnection(parameters=self.__parameters) as connection:
            with AMQPChannel(connection=connection) as channel:
                channel.basic_consume(
                    queue=self.__queue.name,
                    auto_ack=True,
                    on_message_callback=self.__callback,
                    consumer_tag=self.__consumer_tag)
                channel.start_consuming()

    def __configure_exchange(self, channel):
        self.__exchange = AMQPExchange(
            exchange_name=self.__exchange_name,
            exchange_type=self.__exchange_type,
            channel=channel)
        self.__exchange.declare()

    def __configure_queue(self, channel):
        self.__queue = AMQPQueue(channel=channel, name="device_auth")
        self.__queue.declare()
        self.__queue.bind(exchange_name=self.__exchange.name, routing_key=self.__routing_key)

    def __callback(self, channel, method, properties, body):
        dict_body = loads(body.decode("utf-8"))
        print(f"Config response: {dict_body}")
        response = ConfigUpdateResponseSchema().load(dict_body)
        if response.error is not None:
            raise UpdateConfigurationException(response.error)
        if response.changed:
            self.__config = response.config
        channel.basic_cancel(consumer_tag=self.__consumer_tag)