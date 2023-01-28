from dataclasses import dataclass

from yaml import safe_dump, safe_load

from knot_protocol_python.domain.entities.device_entity import DeviceEntity
from knot_protocol_python.infraestructure.adapter.output.DTO.device_schema import \
    DeviceSchema
from knot_protocol_python.infraestructure.adapter.output.repositories.device_repository import \
    DeviceRepository


@dataclass
class DeviceFileRepository(DeviceRepository):
    filepath: str

    def save(self, device: DeviceEntity) -> None:
        serialized_device = DeviceSchema().dump(device)
        with open(self.filepath, "w", encoding="utf-8") as file_writer:
            safe_dump(serialized_device, file_writer)

    def load(self) -> DeviceEntity:
        with open(file=self.filepath, mode="r", encoding="utf-8") as file_reader:
            content = safe_load(file_reader)
        return DeviceSchema().load(content)
