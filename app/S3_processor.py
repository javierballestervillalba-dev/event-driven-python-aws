import boto3
import csv
import io
import os
import time
from typing import Dict, Optional, Tuple
from botocore.exceptions import ClientError

from app.logger import get_logger

logger = get_logger(__name__)

s3_client = boto3.client("s3")
dynamodb = boto3.client("dynamodb")

IDEMPOTENCY_TABLE = os.getenv("IDEMPOTENCY_TABLE", "")


def is_s3_event(event: dict) -> bool:
    return isinstance(event, dict) and "Records" in event


def parse_s3_event(event: dict) -> Dict[str, Optional[str]]:
    """
    Pure function: extracts metadata from the S3 event.
    No side effects, no AWS calls.
    """
    record = event["Records"][0]
    s3_obj = record["s3"]["object"]

    bucket = record["s3"]["bucket"]["name"]
    key = s3_obj["key"]
    etag = s3_obj.get("eTag")
    sequencer = s3_obj.get("sequencer")

    logger.info(
        f"Parsed S3 event | bucket={bucket} key={key} etag={etag} sequencer={sequencer}"
    )

    return {"bucket": bucket, "key": key, "etag": etag, "sequencer": sequencer}


def build_idempotency_key(bucket: str, key: str, etag: str | None, sequencer: str | None) -> str:
    # Preferimos eTag si existe (cambia cuando cambia el contenido)
    uniq = etag or sequencer or "unknown"
    return f"{bucket}#{key}#{uniq}"

def claim_once(pk: str, ttl_seconds: int = 3600) -> bool:
    """
    Attempts to claim processing for this pk using a conditional PutItem.
    True -> claimed (process)
    False -> already claimed/processed (skip)
    """
    if not IDEMPOTENCY_TABLE:
        logger.warning("IDEMPOTENCY_TABLE not set. Running without idempotency.")
        return True

    now = int(time.time())
    expires_at = now + ttl_seconds

    try:
        dynamodb.put_item(
            TableName=IDEMPOTENCY_TABLE,
            Item={
                "pk": {"S": pk},
                "status": {"S": "PROCESSING"},
                "created_at": {"N": str(now)},
                "expires_at": {"N": str(expires_at)},
            },
            ConditionExpression="attribute_not_exists(pk)",
        )
        logger.info(f"Idempotency claim succeeded | pk={pk}")
        return True

    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "ConditionalCheckFailedException":
            logger.warning(f"Idempotency claim failed (duplicate) | pk={pk}")
            return False

        logger.exception(f"Idempotency claim error | pk={pk} code={code}")
        raise

def mark_done(pk: str) -> None:
    if not IDEMPOTENCY_TABLE:
        return

    dynamodb.update_item(
        TableName=IDEMPOTENCY_TABLE,
        Key={"pk": {"S": pk}},
        UpdateExpression="SET #s = :done",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":done": {"S": "DONE"}},
    )
    logger.info(f"Marked DONE | pk={pk}")


def sum_csv_amount(content: str) -> Tuple[int, int]:
    reader = csv.DictReader(io.StringIO(content))

    total = 0
    rows = 0

    for row in reader:
        # row can contain None keys if the CSV is malformed
        rows += 1

        # Normalize headers: " Amount " -> "amount"
        row_norm = {k.strip().lower(): v for k, v in row.items() if k}

        amount_str = row_norm.get("amount")
        if amount_str is None:
            logger.warning(f"Missing 'amount' column | row={row}")
            continue

        try:
            total += int(str(amount_str).strip())
        except ValueError:
            logger.warning(f"Invalid amount value | amount={amount_str} row={row}")
            continue

    return total, rows



def process_s3_object(info: Dict[str, Optional[str]]) -> Dict[str, object]:
    bucket = info["bucket"]
    key = info["key"]
    etag = info.get("etag")
    sequencer = info.get("sequencer")

    if not bucket or not key:
        logger.error(f"Missing bucket/key in S3 info | info={info}")
        return {"skipped": True, "reason": "invalid_event"}

    pk = build_idempotency_key(bucket=bucket, key=key, etag=etag, sequencer=sequencer)

    # Idempotency check BEFORE side effects (reading S3)
    if not claim_once(pk):
        logger.info(f"Duplicate S3 event skipped | bucket={bucket} key={key} pk={pk}")
        return {"skipped": True, "reason": "duplicate", "pk": pk}

    logger.info(f"Reading S3 object | bucket={bucket} key={key}")

    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read().decode("utf-8")
    except Exception:
        logger.exception(f"Failed reading S3 object | bucket={bucket} key={key} pk={pk}")
        raise

    total, rows = sum_csv_amount(content)

    mark_done(pk)

    logger.info(f"Processed CSV | rows={rows} total_amount={total} | pk={pk}")
    return {"skipped": False, "rows": rows, "total_amount": total, "pk": pk}

    


