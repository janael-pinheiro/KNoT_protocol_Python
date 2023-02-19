from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticationRequestDTO:
    id: str
    token: str
