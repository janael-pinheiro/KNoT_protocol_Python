from dataclasses import dataclass


@dataclass(frozen=True)
class UnregistrationReponseDTO:
    id: str
    error: str
