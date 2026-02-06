import logging
from app.config import settings

def get_logger(name: str) -> logging.Logger:

    logger = logging.getLogger(name)
    
    logger.setLevel(settings.LOG_LEVEL)

    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
