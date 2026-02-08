import boto3
import csv
import io

from app.logger import get_logger
from app.config import settings, ConfigError
from app.events import validate_event, EventValidationError



logger = get_logger(__name__)

s3_client = boto3.client("s3")


def is_s3_event(event: dict) -> bool:
        return isinstance(event, dict) and "Records" in event


def parse_s3_event(event: dict) -> dict:
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]
    return {"bucket": bucket, "key": key}


def handler(event, context):
    """
    AWS Lambda entrypoint.
    """
    # 🟢 1. EVENTO S3
    if is_s3_event(event):
        info = parse_s3_event(event)
        logger.info(
            f"S3 event received | bucket={info['bucket']} key={info['key']}"
        )
        response = s3_client.get_object(
            Bucket=info["bucket"],
            Key=info["key"]
        )

        content = response["Body"].read().decode("utf-8")

        logger.info(f"File content:\n{content}")

        #Proceso el csv
        reader = csv.DictReader(io.StringIO(content))

        total = 0
        for row in reader:
            amount = int(row["amount"])
            total += amount

        logger.info(f"Total amount: {total}")


        return {"statusCode": 200, "body": "s3 processed"}
    
    
    # 🟡 2. EVENTOS CUSTOM
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

