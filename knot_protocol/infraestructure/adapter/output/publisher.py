from dataclasses import dataclass
from os import environ
from logging import Logger
from pika import BasicProperties, URLParameters
from pika.adapters.blocking_connection import BlockingChannel
from pika.channel import Channel
from pika.exceptions import ConnectionClosedByBroker, UnroutableError
from tenacity import retry, retry_if_exception_type
from tenacity.wait import wait_exponential

from knot_protocol.domain.boundary.output.publisher import Publisher
from knot_protocol.infraestructure.adapter.input.connection import (
    AMQPChannel, AMQPConnection)


@dataclass
class AMQPPublisher(Publisher):
    channel: BlockingChannel
    exchange_name: str
    routing_key: str
    channel: Channel
    properties: BasicProperties
    logger: Logger
    content: str = ""

    @retry(
        retry=retry_if_exception_type(ConnectionClosedByBroker),
        wait=wait_exponential(multiplier=1, min=4, max=10))
    def publish(self):
        if self.channel.connection.is_closed:
            self.logger.info("Publisher connection closed! Reconnecting...")
            connection = AMQPConnection(URLParameters(environ.get("AMQP_URL"))).create()
            self.channel = AMQPChannel(connection=connection).create()
            self.channel.confirm_delivery()

        try:
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key,
                body=self.content,
                properties=self.properties,
                mandatory=True)
        except UnroutableError:
            print('Message could not be confirmed')
