from pika import BlockingConnection
from pika.connection import Parameters
from pika.channel import Channel
from dataclasses import dataclass


@dataclass
class AMQPConnection:
    parameters: Parameters

    def create(self) -> BlockingConnection:
        return BlockingConnection(self.parameters)

@dataclass
class AMQPChannel:
    connection: BlockingConnection

    def create(self) -> Channel:
        return self.connection.channel()


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
