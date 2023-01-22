from knot_protocol_python.domain.boundary.output.publisher import Publisher


class RabbitMQPublisherGateway(Publisher):
    def publish(self):
        return super().publish()
