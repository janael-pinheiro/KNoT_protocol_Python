from dataclasses import dataclass
from typing import List

from knot_protocol_python.domain.DTO.device_configuration import ConfigurationDTO


@dataclass
class UpdateConfigRequest:
    id: str
    config: List[ConfigurationDTO]
