from dataclasses import dataclass

from knot_protocol_python.domain.DTO.device_configuration import ConfigurationDTO


@dataclass
class ConfigurationUpdateResponseDTO:
    id: str
    config: ConfigurationDTO
    changed: bool
    error: str
