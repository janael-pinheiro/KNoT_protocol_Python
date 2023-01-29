from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class DataPointDTO:
    sensor_id: int
    value: Union[float, int]
    timestamp: str
