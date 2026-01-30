from app.logger import get_logger
from app.config import settings

logger = get_logger(__name__)

def main():
    logger.info("Service started")
    logger.info(
        "Running service",
        extra={
            "service": settings.SERVICE_NAME,
            "environment": settings.ENVIRONMENT,
        },
    )

if __name__ == "__main__":
    main()

