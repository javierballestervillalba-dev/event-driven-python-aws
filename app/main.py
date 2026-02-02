from app.logger import get_logger
from app.config import settings, ConfigError
from app.events import validate_event, EventValidationError


logger = get_logger(__name__)

def handler(event, context):
    """
    AWS Lambda entrypoint.
    """
    try:
        logger.info(f"Event received | event={event}")

        validate_event(event)

        event_type = event["type"]
        payload = event["payload"]

        handler_fn = EVENT_HANDLERS.get(event_type)

        if not handler_fn:
            raise EventValidationError(
                f"No handler registered for event type '{event_type}'"
            )

        handler_fn(payload)

        logger.info("Event processed successfully")
        return {"statusCode": 200, "body": "ok"}

    except EventValidationError as e:
        logger.error(f"Invalid event: {e}")
        return {"statusCode": 400, "body": str(e)}

    except Exception as e:
        logger.exception("Unhandled error processing event")
        return {"statusCode": 500, "body": "internal error"}
    

def handle_user_registered(payload: dict) -> None:
    logger.info(
        f"Handling UserRegistered | user_id={payload.get('user_id')}"
    )


def handle_order_created(payload: dict) -> None:
    logger.info(
        f"Handling OrderCreated | order_id={payload.get('order_id')} amount={payload.get('amount')}"
    )

EVENT_HANDLERS = {
    "UserRegistered": handle_user_registered,
    "OrderCreated": handle_order_created,
}



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

