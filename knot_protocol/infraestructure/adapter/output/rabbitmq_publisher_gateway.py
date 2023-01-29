from knot_protocol.domain.boundary.output.publisher import Publisher


class RabbitMQPublisherGateway(Publisher):
    def publish(self):
        return super().publish()
