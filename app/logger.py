import logging
from app.config import settings

def get_logger(name: str) -> logging.Logger:

    logger = logging.getLogger(name)

    if logger.handlers:

        return logger
    
    logger.setLevel(settings.LOG_LEVEL)

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
