"""Helpers to deal with simple data."""
from slugify import slugify
from uuid import uuid4


def generate_uuid() -> str:
    """Generate an uuid4.

    :returns: A UUID4 string
    """
    return str(uuid4())


def generate_slug(value: str) -> str:
    """Given a value, return the slugified version of it.

    :param value: A string to be converted to a slug
    :return: A url-friendly slug of a value.
    """
    return slugify(value)


def generate_contextual_slug(context: dict) -> str:
    """Given a context, calculate the slug for it.

    :param context: Dictionary containing some values like id and title.
    :return: A url-friendly slug of a value.
    """
    obj_id = context.get('id', '')
    if obj_id:
        # Return just the first 8 chars of an uuid
        obj_id = str(obj_id)[:8]
    else:
        obj_id = ''
    title = context.get('title', '')
    slug = '{obj_id}-{title}'.format(
        obj_id=obj_id,
        title=generate_slug(title)
    )
    return slug
