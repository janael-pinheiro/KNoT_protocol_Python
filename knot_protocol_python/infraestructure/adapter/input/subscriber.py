from pika import URLParameters
from time import sleep
from json import loads

from knot_protocol_python.infraestructure.adapter.input.connection import AMQPConnection, AMQPChannel
from knot_protocol_python.infraestructure.adapter.input.connection import AMQPExchange, AMQPQueue
from knot_protocol_python.domain.boundary.input.subscriber import Subscriber
from knot_protocol_python.infraestructure.adapter.input.DTO.device_registration_response_DTO import DeviceRegistrationResponseDTO
from knot_protocol_python.infraestructure.adapter.input.DTO.device_auth_response_DTO import AuthDeviceResponseDTO
from knot_protocol_python.domain.exceptions.device_exception import AlreadyRegisteredDeviceExcepiton, AuthenticationErrorException


class RegisterSubscriber(Subscriber):

    def __init__(self, parameters: URLParameters) -> None:
        self.__exchange_name = "device"
        self.__exchange_type = "direct"
        self.__routing_key = "device.registered"
        self.__consumer_tag = "device_register"
        self.__parameters = parameters
        self.__connection = None
        self.__channel = None
        self.__exchange = None
        self.__queue = None
        self.__token = None

    def subscribe(self):
        self.__start()
        return self.__token

    def unsubscribe(self):
        ...

    def __start(self):
        self.__create_connection()
        self.__channel.basic_consume(
            queue=self.__queue.name,
            auto_ack=True,
            on_message_callback=self.__callback,
            consumer_tag=self.__consumer_tag)
        self.__channel.start_consuming()

    def __create_connection(self):
        self.__connection = AMQPConnection(parameters=self.__parameters).create()
        self.__channel = AMQPChannel(connection=self.__connection).create()
        self.__exchange = AMQPExchange(
            exchange_name=self.__exchange_name,
            exchange_type=self.__exchange_type,
            channel=self.__channel)
        self.__exchange.declare()
        self.__queue = AMQPQueue(channel=self.__channel, name="device_registered")
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
        self.__connection = None
        self.__channel = None
        self.__exchange = None
        self.__queue = None

    def subscribe(self):
        self.__start()

    def unsubscribe(self):
        ...

    def __start(self):
        self.__create_connection()
        self.__channel.basic_consume(
            queue=self.__queue.name,
            auto_ack=True,
            on_message_callback=self.__callback,
            consumer_tag=self.__consumer_tag)
        self.__channel.start_consuming()

    def __create_connection(self):
        self.__connection = AMQPConnection(parameters=self.__parameters).create()
        self.__channel = AMQPChannel(connection=self.__connection).create()
        self.__exchange = AMQPExchange(
            exchange_name=self.__exchange_name,
            exchange_type=self.__exchange_type,
            channel=self.__channel)
        self.__exchange.declare()
        self.__queue = AMQPQueue(channel=self.__channel, name="device_auth")
        self.__queue.declare()
        self.__queue.bind(exchange_name=self.__exchange.name, routing_key=self.__routing_key)

    def __callback(self, channel, method, properties, body):
        dict_body = loads(body.decode("utf-8"))
        print(f"Auth response: {dict_body}")
        response = AuthDeviceResponseDTO().load(dict_body)
        if response.error is not None:
            raise AuthenticationErrorException(response.error)
        channel.basic_cancel(consumer_tag=self.__consumer_tag)
