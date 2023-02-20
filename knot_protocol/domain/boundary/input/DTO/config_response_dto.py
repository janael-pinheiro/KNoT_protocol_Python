from dataclasses import dataclass

from knot_protocol.domain.boundary.output.DTO.schema import SchemaDTO


@dataclass(frozen=True)
class ConfigurationUpdateResponseDTO:
    id: str
    config: SchemaDTO
    changed: bool
    error: str
