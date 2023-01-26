from pika.adapters.blocking_connection import BlockingChannel
from pika.channel import Channel
from pika import BasicProperties
from dataclasses import dataclass

from knot_protocol_python.domain.boundary.output.publisher import Publisher


@dataclass
class AMQPPublisher(Publisher):
    channel: BlockingChannel
    exchange_name: str
    routing_key: str
    channel: Channel
    properties: BasicProperties
    content: str = ""

    def publish(self):
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=self.routing_key,
            body=self.content,
            properties=self.properties)
