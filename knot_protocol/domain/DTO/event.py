from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class Event:
    change: bool
    time_seconds: int
    lower_threshold: Union[float, int]
    upper_threshold: Union[float, int]


class EventFactory:
    @classmethod
    def create(
            cls,
            change: bool,
            time_seconds: int,
            lower_threshold: Union[float, int],
            upper_threshold: Union[float, int]) -> Event:
        return Event(
            change=change,
            time_seconds=time_seconds,
            lower_threshold=lower_threshold,
            upper_threshold=upper_threshold)