from enum import Enum


class KNoTExchange(Enum):
    device_exchange = "device"
    data_sent_exchange = "data.sent"


class KNoTRoutingKey(Enum):
    registered_device = "device.registered"
    updated_schema = "device.config.updated"


class KNoTValueType(Enum):
    INT = 1
    FLOAT = 2
    BOOL = 3
    STRING = 4


class KNoTPatterns(Enum):
    TOKEN = "[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"