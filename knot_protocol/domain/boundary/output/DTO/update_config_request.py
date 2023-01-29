from dataclasses import dataclass
from typing import List

from knot_protocol.domain.DTO.schema import SchemaDTO


@dataclass(frozen=True)
class UpdateConfigRequest:
    id: str
    config: List[SchemaDTO]
