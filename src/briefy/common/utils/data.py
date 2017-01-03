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
    if not isinstance(context, dict):
        context = context.current_parameters

    obj_id = context.get('id', '')
    title = context.get('title', '')

    slug_id = str(obj_id)[:8] if obj_id else ''
    slug_title = generate_slug(title) if title else ''

    if slug_id and slug_title:
        slug = '{slug_id}-{slug_title}'.format(
            slug_id=slug_id,
            slug_title=slug_title
        )
    else:
        slug = slug_id if slug_id else slug_title
    return slug
