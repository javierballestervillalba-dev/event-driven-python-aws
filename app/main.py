from app.logger import get_logger
from app.config import settings, ConfigError
from app.events import validate_event, EventValidationError
from app.S3_processor import is_s3_event, parse_s3_event, process_s3_object


logger = get_logger(__name__)



def handler(event, context):

    request_id = getattr(context, "aws_request_id", "local")
    logger.info(f"Start | request_id={request_id}")


    # 1) S3 event
    if is_s3_event(event):
        info = parse_s3_event(event)
        result = process_s3_object(info["bucket"], info["key"])
        return {"statusCode": 200, "body": f"s3 processed {result}"}

    # 2) Custom events
    try:
        validate_event(event)
        event_type = event["type"]
        payload = event["payload"]

        handler_fn = EVENT_HANDLERS.get(event_type)
        if not handler_fn:
            raise EventValidationError(f"No handler registered for '{event_type}'")

        handler_fn(payload)
        return {"statusCode": 200, "body": "ok"}

    except EventValidationError as e:
        logger.error(f"Invalid event: {e}")
        return {"statusCode": 400, "body": str(e)}
    except Exception:
        logger.exception("Unhandled error")
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

