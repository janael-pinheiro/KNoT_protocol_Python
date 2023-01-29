from dataclasses import dataclass


@dataclass(frozen=True)
class SchemaDTO:
    value_type: int
    unit: int
    type_id: int
    name: str
