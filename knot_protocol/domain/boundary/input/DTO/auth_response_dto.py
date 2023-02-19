from dataclasses import dataclass


@dataclass(frozen=True)
class AuthResponseDTO:
    id: str
    error: str = ""
