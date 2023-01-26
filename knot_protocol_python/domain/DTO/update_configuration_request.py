from dataclasses import dataclass
from typing import List

from knot_protocol_python.domain.DTO.device_configuration import SchemaDTO


@dataclass
class UpdateConfigurationRequest:
    device_id: str
    configuration: List[SchemaDTO]
