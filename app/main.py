from app.logger import get_logger
from app.config import settings, ConfigError

logger = get_logger(__name__)

def handler(event, context):
    """
    AWS Lambda entrypoint.
    event: dict
    context: Lambda ciontext object
    """
    logger.info(f"Lambda invoked | event={event}")

    #Por ahora solo devolvemos OK
    return {"statusCode": 200, "body": "ok"}

def main() -> None:
    try:
        logger.info("Service started")
        logger.info(
            f"Running service | service={settings.SERVICE_NAME} env={settings.ENVIRONMENT}"
        )
        # Simulación de "lógica"
        # En los próximos días aquí procesaremos eventos reales
        logger.info("Ready to process events")

    except ConfigError as e:
        # Config mala -> error claro y salida
        logger.error(f"Configuration error: {e}")
        raise

    except Exception as e:
        #Cualquier otro error inesperado
        logger.exception(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()

