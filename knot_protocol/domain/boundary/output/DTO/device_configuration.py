from dataclasses import dataclass
from knot_protocol.domain.boundary.output.DTO.schema import SchemaDTO
from knot_protocol.domain.boundary.output.DTO.event import Event


@dataclass(frozen=True, eq=False)
class ConfigurationDTO:
    sensor_id: int
    schema: SchemaDTO
    event: Event

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConfigurationDTO):
            return False
        return self.sensor_id == other.sensor_id

    def __hash__(self) -> int:
        return hash(self.sensor_id)


class ConfigurationFactory:
    @classmethod
    def create(
            cls,
            sensor_id: int,
            schema: SchemaDTO,
            event: Event) -> ConfigurationDTO:
        return ConfigurationDTO(
            sensor_id=sensor_id,
            schema=schema,
            event=event)
