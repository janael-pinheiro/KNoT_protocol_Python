from dataclasses import dataclass


@dataclass
class UnregistrationReponseDTO:
    id: str
    error: str
