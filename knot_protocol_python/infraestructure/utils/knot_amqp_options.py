from enum import Enum


class KNoTExchange(Enum):
    device_exchange = "device"
    data_sent_exchange = "data.sent"


class KNoTRoutingKey(Enum):
    registered_device = "device.registered"
    updated_schema = "device.config.updated"
