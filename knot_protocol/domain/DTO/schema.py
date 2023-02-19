from dataclasses import dataclass


@dataclass(frozen=True)
class SchemaDTO:
    value_type: int
    unit: int
    type_id: int
    name: str


class SchemaFactory:
    @classmethod
    def create(
            cls,
            value_type: int,
            unit: int,
            type_id: int,
            name: str) -> SchemaDTO:
        return SchemaDTO(
            name=name,
            value_type=value_type,
            type_id=type_id,
            unit=unit)
