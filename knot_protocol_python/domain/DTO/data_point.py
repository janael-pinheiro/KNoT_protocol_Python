from dataclasses import dataclass
from typing import Union


@dataclass
class DataPointDTO:
    sensor_id: int
    value: Union[float, int]
    timestamp: str
