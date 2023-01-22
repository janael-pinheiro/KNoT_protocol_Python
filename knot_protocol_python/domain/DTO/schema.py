from dataclasses import dataclass


@dataclass
class Schema:
    value_type: int
    unit: int
    type_id: int
    name: str
