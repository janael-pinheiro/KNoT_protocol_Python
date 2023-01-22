from dataclasses import dataclass
from knot_protocol_python.domain.DTO.schema import Schema
from knot_protocol_python.domain.DTO.event import Event


@dataclass
class ConfigurationDTO:
    sensor_id: int
    schema: Schema
    event: Event
