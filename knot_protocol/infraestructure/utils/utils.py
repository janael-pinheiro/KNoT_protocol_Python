from json import loads
from typing import Dict
from uuid import uuid4
import yaml
from knot_protocol.infraestructure.adapter.output.DTO.device_schema import SchemaConfiguration


def json_parser(json_content: Dict[str, str]) -> Dict[str, str]:
    return loads(json_content.decode("utf-8"))


def generate_consumer_tag() -> str:
    return str(uuid4()).replace('-', '')


def load_device_schema_from_yaml_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as file_reader:
        yaml_content = yaml.safe_load(file_reader)
    return SchemaConfiguration().load(yaml_content)
