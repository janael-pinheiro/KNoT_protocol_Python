from dataclasses import dataclass
from knot_protocol.domain.DTO.schema import SchemaDTO
from knot_protocol.domain.DTO.event import Event


@dataclass(frozen=True)
class ConfigurationDTO:
    sensor_id: int
    schema: SchemaDTO
    event: Event
