from dataclasses import dataclass


@dataclass(frozen=True)
class RegistrationRequest:
    id: str
    name: str
