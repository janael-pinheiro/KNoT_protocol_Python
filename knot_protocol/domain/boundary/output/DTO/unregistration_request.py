from dataclasses import dataclass


@dataclass(frozen=True)
class UnregistrationRequest:
    id: str
    name: str
