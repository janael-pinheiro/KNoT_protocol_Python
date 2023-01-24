from pika import BlockingConnection
from pika.connection import Parameters
from pika.channel import Channel


class AMQPConnection:
    def __init__(self, parameters: Parameters) -> None:
        self.__parameters = parameters
        self.__connection = None

    def __enter__(self):
        self.__connection = BlockingConnection(self.__parameters)
        return self.__connection

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.__connection.close()


class AMQPChannel:
    def __init__(self, connection: BlockingConnection) -> None:
        self.__connection = connection
        self.__channel = None

    def __enter__(self):
        self.__channel = self.__connection.channel()
        return self.__channel

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.__channel.close()


class AMQPExchange:
    def __init__(
            self,
            exchange_name: str,
            exchange_type: str,
            channel: Channel) -> None:
        self.__name = exchange_name
        self.__type = exchange_type
        self.__channel = channel

    def declare(self) -> None:
        self.__channel.exchange_declare(self.__name, self.__type, durable=True, auto_delete=False)
    
    @property
    def name(self) -> str:
        return self.__name


class AMQPQueue:
    def __init__(self, name: str, channel: Channel) -> None:
        self.__name = name
        self.__channel = channel

    def declare(self) -> None:
        self.__channel.queue_declare(self.__name)

    def bind(self, exchange_name: str, routing_key) -> None:
        self.__channel.queue_bind(self.__name, exchange_name, routing_key=routing_key)

    @property
    def name(self) -> str:
        return self.__name
