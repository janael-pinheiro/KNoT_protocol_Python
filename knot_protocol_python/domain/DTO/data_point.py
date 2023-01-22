from dataclasses import dataclass
from typing import Union


@dataclass
class DataPointDTO:
    sensorID: int
    value: Union[float, int]
    timestamp: str
