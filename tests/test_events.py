import pytest
from app.events import validate_event, EventValidationError
from app.main import handler


def test_valid_event_passes():
    event = {
        "source": "test",
        "type": "UserRegistered",
        "payload": {"user_id": 1},
    }

    # Si no lanza excepción, el test pasa
    validate_event(event)


def test_event_missing_fields_fails():
    event = {"type": "UserRegistered"}

    with pytest.raises(EventValidationError):
        validate_event(event)


def test_event_with_unknown_type_fails():
    event = {
        "source": "test",
        "type": "SomethingElse",
        "payload": {},
    }

    with pytest.raises(EventValidationError):
        validate_event(event)

def test_handler_order_created_ok():
    event = {
        "source": "test",
        "type": "OrderCreated",
        "payload": {"order_id": 123, "amount": 50},
    }

    response = handler(event, None)

    assert response["statusCode"] == 200


def test_handler_invalid_event_returns_400():
    event = {"type": "OrderCreated"}

    response = handler(event, None)

    assert response["statusCode"] == 400


def test_handler_event_without_registered_handler():
    event = {
        "source": "test",
        "type": "PaymentFailed",
        "payload": {},
    }

    response = handler(event, None)

    assert response["statusCode"] == 400

