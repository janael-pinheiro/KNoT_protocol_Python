from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class DataPointDTO:
    sensor_id: int
    value: Union[float, int]
    timestamp: str


class DataPointFactory:
    @classmethod
    def create(
        cls,
        sensor_id: int,
        value: Union[float, int],
        timestamp: str) -> DataPointDTO:
        return DataPointDTO(
            sensor_id=sensor_id,
            value=value,
            timestamp=timestamp)
