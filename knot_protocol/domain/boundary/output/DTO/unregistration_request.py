from dataclasses import dataclass


@dataclass
class UnregistrationRequest:
    id: str
    name: str
