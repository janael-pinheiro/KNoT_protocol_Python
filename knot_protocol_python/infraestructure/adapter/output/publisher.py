from pika.adapters.blocking_connection import BlockingChannel
from pika import BasicProperties

from knot_protocol_python.domain.boundary.output.publisher import Publisher


class RegisterPublisher(Publisher):
    def __init__(
            self,
            channel: BlockingChannel,
            knot_token: str) -> None:
        self.__exchange_name = "device"
        self.__routing_key = "device.register"
        self.__channel = channel
        self.__properties = BasicProperties(
            headers={"Authorization": f"{knot_token}"})

    def publish(self):
        self.__channel.basic_publish(
            exchange=self.__exchange_name,
            routing_key=self.__routing_key,
            body=self.__content,
            properties=self.__properties)

    @property
    def content(self) -> str:
        return self.__content

    @content.setter
    def content(self, content: str) -> None:
        self.__content = content


class AuthPublisher(Publisher):
    def __init__(
            self,
            channel: BlockingChannel,
            knot_token: str) -> None:
        self.__exchange_name = "device"
        self.__routing_key = "device.auth"
        self.__reply_to = "device-auth-rpc"
        self.__correlation_id = "auth_correlation_id"
        self.__channel = channel
        self.__properties = BasicProperties(
            headers={"Authorization": f"{knot_token}"},
            reply_to=self.__reply_to,
            correlation_id=self.__correlation_id)

    def publish(self):
        print(f"Auth: {self.__content}")
        self.__channel.basic_publish(
            exchange=self.__exchange_name,
            routing_key=self.__routing_key,
            body=self.__content,
            properties=self.__properties)

    @property
    def content(self) -> str:
        return self.__content

    @content.setter
    def content(self, content: str) -> None:
        self.__content = content


class UpdateConfigPublisher(Publisher):
    def __init__(
            self,
            channel: BlockingChannel,
            knot_token: str) -> None:
        self.__exchange_name = "device"
        self.__routing_key = "device.config.sent"
        self.__channel = channel
        self.__properties = BasicProperties(
            headers={"Authorization": f"{knot_token}"})

    def publish(self):
        self.__channel.basic_publish(
            exchange=self.__exchange_name,
            routing_key=self.__routing_key,
            body=self.__content,
            properties=self.__properties)

    @property
    def content(self) -> str:
        return self.__content

    @content.setter
    def content(self, content: str) -> None:
        self.__content = content


class DataPublisher(Publisher):
    def __init__(
            self,
            channel: BlockingChannel,
            knot_token: str) -> None:
        self.__exchange_name = "data.sent"
        self.__routing_key = ""
        self.__channel = channel
        self.__properties = BasicProperties(
            headers={"Authorization": f"{knot_token}"})

    def publish(self):
        self.__channel.basic_publish(
            exchange=self.__exchange_name,
            routing_key=self.__routing_key,
            body=self.__content,
            properties=self.__properties)

    @property
    def content(self) -> str:
        return self.__content

    @content.setter
    def content(self, content: str) -> None:
        self.__content = content
