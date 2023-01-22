from dataclasses import dataclass
from typing import List

from knot_protocol_python.domain.DTO.device_configuration import ConfigurationDTO


@dataclass
class UpdateConfigurationRequest:
    device_id: str
    configuration: List[ConfigurationDTO]
