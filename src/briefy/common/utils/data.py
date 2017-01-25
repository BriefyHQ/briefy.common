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


class Objectify:
    """Alows using values of nested JSON-like data structures as Python objects.

    Makes SQS and HTTP payloads easy to use without goign too full model
    declaration.

    """

    def __init__(self, dct: (dict, list)):
        """Initalizer."""
        self.dct = dct

    def _normalize_attr(self, attr):
        """Allow use of numbers prefixed by underscores as attributes when the object is a list."""
        if attr.startswith("_") and attr.strip('_').isdigit():
            attr = int(attr[1:].replace('_', '-'))
        return attr

    def __getattr__(self, attr):
        """Retrieve attribute from underliying object."""
        attr = self._normalize_attr(attr)
        result = self.dct.__getitem__(attr)
        if isinstance(result, (dict, list)):
            return Objectify(result)
        return result

    def __setattr__(self, attr, value):
        """Set apropriate attribute on underlying object."""
        if attr == 'dct' or hasattr(self, attr):
            return super().__setattr__(attr, value)
        attr = self._normalize_attr(attr)
        self.dct.__setitem__(attr, value)

    def __repr__(self):
        """Representation."""
        return('Objectify({})'.format(self.dct))

    def __bool__(self):
        """Assure truthy value is False when appropriate."""
        return bool(self.dct)

