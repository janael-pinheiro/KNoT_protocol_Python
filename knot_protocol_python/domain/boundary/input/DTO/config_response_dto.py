from dataclasses import dataclass

from knot_protocol_python.domain.DTO.device_configuration import SchemaDTO


@dataclass
class ConfigurationUpdateResponseDTO:
    id: str
    config: SchemaDTO
    changed: bool
    error: str
