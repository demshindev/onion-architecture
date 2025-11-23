import logging
import sys

from src.infrastructure.config import settings


def setup_logger(name: str = "test_api") -> logging.Logger:
    log = logging.getLogger(name)
    
    if log.handlers:
        return log
    
    log.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.propagate = False
    
    return log


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(record, "request_id", "N/A")
        return True


logger = setup_logger()
logger.addFilter(RequestIDFilter())

