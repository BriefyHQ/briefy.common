"""Helpers to deal with simple data."""
from slugify import slugify
from uuid import uuid4


def generate_uuid():
    """Generate an uuid4.

    :returns: A UUID4 string
    :rtype: str
    """
    return str(uuid4())


def generate_slug(value: str) -> str:
    """Given a value, return the slugified version of it.

    :param value: A string to be converted to a slug
    :return: A url-friendly slug of a value.
    """
    return slugify(value)
