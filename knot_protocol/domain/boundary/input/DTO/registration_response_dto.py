from dataclasses import dataclass


@dataclass(frozen=True)
class RegistrationResponseDTO:
    id: str
    name: str
    token: str
    error: str = ""
