import logging

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO)

def logger_factory() -> logging.Logger:
    return logging.getLogger()
