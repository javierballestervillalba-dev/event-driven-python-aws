# event-driven-python-aws (AWS-style)

Python service designed with an event-driven architecture, inspired by AWS Lambda and EventBridge.
The project focuses on clean structure, configuration validation, event routing, and testability.

## Architecture Overview

This service follows an event-driven design:

- Events are received by a single entrypoint (`handler`)
- Events are validated against a strict contract
- Events are routed to specific handlers based on their type
- Each handler is responsible for a single event type

## Event Contract Example


{
  "source": "ecommerce.orders",
  "type": "OrderCreated",
  "payload": {
    "order_id": 123,
    "amount": 49.90
  }
}

## Run Locally

Activate the virtual environment:

venv\Scripts\Activate.ps1

Run the service locally:

python -m app.main

Invoke the Lambda-style handler manually:

python -c "from app.main import handler; print(handler({...}, None))"


## Tests

Tests are written using pytest and cover:

- Event validation
- Event routing
- Handler responses

Run tests with:

pytest


## Design Decisions

- Configuration is validated at startup (fail-fast)
- Events are immutable and validated before processing
- Routing is handled via a handler map instead of conditional logic
- Business logic is separated from infrastructure concerns


## AWS Mapping

This project mirrors AWS concepts:

- `handler` → AWS Lambda entrypoint
- Event structure → EventBridge events
- Event routing → EventBridge rules
- Logging → CloudWatch-style logs
