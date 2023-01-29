from knot_protocol.domain.boundary.input.subscriber import Subscriber


class RabbitMQSubscriberGateway(Subscriber):
    def subscribe(self):
        return super().subscribe()
