"""Helpers to deal with simple data."""
from uuid import uuid4


def generate_uuid():
    """Generate an uuid4.

    :returns: A UUID4 string
    :rtype: str
    """
    return str(uuid4())
