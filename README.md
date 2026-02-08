# event-driven-python-aws

Python service designed with an **event-driven architecture**, inspired by AWS Lambda and EventBridge, and deployed on **AWS Lambda** with **real S3 triggers**.

The project focuses on clean structure, configuration validation, event routing, robustness against bad input data, and reproducible deployments.



## Architecture Overview

This service follows an event-driven design with a **single Lambda entrypoint** acting as a router.

### High-level flow

┌───────────┐
│ S3 │
│ Bucket │
└─────┬─────┘
│ ObjectCreated
▼
┌───────────────┐
│ AWS Lambda │
│ Python │
│ event-driven │
└─────┬─────────┘
│
▼
┌───────────────┐
│ CloudWatch │
│ Logs & Metrics│
└───────────────┘


### Core principles

- Events are received by a single entrypoint (`handler`)
- The handler detects the event source (AWS-native vs custom)
- Events are validated before processing
- Logic is routed to dedicated handlers
- Business logic is separated from infrastructure concerns

---

##  Supported Event Types

### 1️⃣ AWS S3 Events (real trigger)

- Triggered by `ObjectCreated` events
- The Lambda:
  - Extracts `bucket` and `key`
  - Reads the object from S3 using `GetObject`
  - Processes CSV content defensively
  - Logs results and warnings to CloudWatch

### 2️⃣ Custom Events (EventBridge-style)

Custom events follow a strict contract and are routed internally.

#### Event Contract Example

```json
{
  "source": "ecommerce.orders",
  "type": "OrderCreated",
  "payload": {
    "order_id": 123,
    "amount": 49.90
  }
}

```
# Project Structure
.
├── app/
│   ├── main.py           # Lambda handler (router)
│   ├── s3_processor.py   # S3-specific processing logic
│   ├── logger.py         # Centralized logging
│   ├── config.py         # Environment-based configuration
│   └── events.py         # Custom event validation & routing
│
├── lambda_wrapper/
│   └── main.py           # Lambda entrypoint wrapper (main.handler)
│
├── build_lambda_zip.py   # Build script for Lambda ZIP
├── README.md
└── .gitignore

# CSV Processing Logic

Expected CSV format:

id,name,amount
1,Alice,10
2,Bob,20

Processing behavior

* Headers are normalized (strip + lower)
* Missing or invalid rows are skipped
* The Lambda never fails due to bad data
* Warnings are logged for malformed rows
* Aggregated results are logged (rows processed, total amount)


# Run Locally

Activate the virtual environment:

```bash

venv\Scripts\Activate.ps1
```
Run the service locally:

```bash
python -m app.main
```

Invoke the Lambda-style handler manually:

```bash
python -c "from app.main import handler; print(handler({...}, None))"
```

# Tests

Tests are written using pytest and cover:

* Event validation
* Event routing
* Handler responses

Run tests with:

```bash
pytest
```

# IAM Permissions

The Lambda uses an execution role with least privilege.

Required permission to read from S3:

```json
{
  "Effect": "Allow",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::<BUCKET_NAME>/*"
}
```

No credentials are hardcoded.

# Logging & Observability

* Centralized logging using Python logging
* Single handler (no duplicated logs)
* AWS request ID used for correlation
* Metrics available in CloudWatch:
  * Invocations
  * Errors
  * Duration


# Build & Deployment

The Lambda code is deployed as a reproducible ZIP artefact.

  # Build the ZIP
  ```bash
  python build_lambda_zip.py
```

The script:

* Deletes the previous ZIP
* Packages app/ and the Lambda wrapper
* Ensures correct Python package structure

Code is never edited in the AWS console to avoid inconsistencies.

# Troubleshooting
❌ No module named 'app'
* ZIP built incorrectly
* Editing code in the AWS console broke the package
✔️ Solution: rebuild ZIP locally and redeploy

❌ AccessDenied when reading S3
* Missing s3:GetObject permission
✔️ Solution: attach IAM policy to Lambda execution role

❌ KeyError: 'amount'
* CSV missing expected column
* Header formatting issues
✔️ Solution: defensive parsing and header normalization

# Design Decisions

* Event-driven architecture with a single entrypoint
* Clear separation between routing and business logic
* Defensive data processing
* Fail-fast configuration validation
* Least-privilege IAM policies
* Reproducible deployments via build artefacts