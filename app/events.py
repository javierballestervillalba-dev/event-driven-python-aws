from typing import Dict

class EventValidationError(Exception):
    """Raised when an incoming event is invalid"""
    pass

def validate_event(event: Dict) -> None:
    if not isinstance(event, dict):
        raise EventValidationError("Event must be a dict")
    required_fields = {"source", "type", "payload"}
    missing = required_fields - event.keys()

    if missing:
        raise EventValidationError(f"Missing fields: {missing}")
    
    allowed_types = {"UserRegistered", "OrderCreated"}
    if event["type"] not in allowed_types:
        raise EventValidationError(
            f"Unsupported event type: {event['type']}"
        )
