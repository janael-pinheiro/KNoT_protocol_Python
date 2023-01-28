from json import loads
from typing import Dict
import logging

logging.basicConfig(
    filemode="a",
    filename="knot_protocol.log",
    format="%(asctime)s %(message)s",
    level=logging.INFO)

def json_parser(json_content: Dict[str, str]) -> Dict[str, str]:
    return loads(json_content.decode("utf-8"))


def logger_factory() -> logging.Logger:
    return logging.getLogger()
