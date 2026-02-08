import boto3
import csv
import io
from typing import Dict

from app.logger import get_logger

logger = get_logger(__name__)
s3_client = boto3.client("s3")


def is_s3_event(event: dict) -> bool:
    return isinstance(event, dict) and "Records" in event


def parse_s3_event(event: dict) -> Dict[str, str]:
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]
    return {"bucket": bucket, "key": key}


def process_s3_object(bucket: str, key: str) -> Dict[str, str]:
    logger.info(f"Reading S3 object | bucket={bucket} key={key}")

    response = s3_client.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")

    total, rows = sum_csv_amount(content)

    logger.info(f"Processed CSV | rows={rows} total_amount={total}")
    return {"rows": str(rows), "total_amount": str(total)}


def sum_csv_amount(content: str) -> tuple[int, int]:
    reader = csv.DictReader(io.StringIO(content))

    total = 0
    rows = 0

    for row in reader:
        rows += 1

        # normaliza headers
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
