from dataclasses import dataclass
from typing import List

from knot_protocol.domain.boundary.output.DTO.data_point import DataPointDTO


@dataclass(frozen=True)
class PublishingData:
    id: str
    data: List[DataPointDTO]
