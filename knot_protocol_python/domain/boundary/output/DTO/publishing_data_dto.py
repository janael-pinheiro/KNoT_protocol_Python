from dataclasses import dataclass
from typing import List

from knot_protocol_python.domain.DTO.data_point import DataPointDTO


@dataclass
class PublishingData:
    id: str
    data: List[DataPointDTO]
