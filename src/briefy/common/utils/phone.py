"""Module to deal with Phone numbers validation."""
import phonenumbers


def validate_phone(value: str) -> bool:
    """Validate a phone number."""
    try:
        number = phonenumbers.parse(value)
    except phonenumbers.NumberParseException:
        status = False
    else:
        status = phonenumbers.is_valid_number(number)
    return status
