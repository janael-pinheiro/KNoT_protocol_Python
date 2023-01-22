from dataclasses import dataclass
from typing import Union

@dataclass
class Event:
    change: bool
    time_seconds: int
    lower_threshold: Union[float, int]
    upper_threshold: Union[float, int]
