from knot_protocol_python.domain.boundary.input.subscriber import Subscriber


class RabbitMQSubscriberGateway(Subscriber):
    def subscribe(self):
        return super().subscribe()
