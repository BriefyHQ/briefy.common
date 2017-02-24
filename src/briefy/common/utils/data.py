"""Helpers to deal with simple data."""
from slugify import slugify
from uuid import uuid4

import inspect


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

    Makes SQS and HTTP payloads easy to use without going too full model
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

    def __getitem__(self, attr):
        """Retrieve attribute from data container.

        If the retrieved value is itself a container, wrap it
        into an "Objectify" instance.
        """
        result = self.dct.__getitem__(attr)
        if isinstance(result, (dict, list)):
            return Objectify(result)
        return result

    def __getattr__(self, attr):
        """Retrieve attribute from underliying object."""
        attr = self._normalize_attr(attr)
        try:
            return self.__getitem__(attr)
        except (KeyError, IndexError) as error:
            raise AttributeError from error

    def __setattr__(self, attr, value):
        """Set apropriate attribute on underlying object."""
        if attr == 'dct' or attr in self.__dict__:
            return super().__setattr__(attr, value)
        attr = self._normalize_attr(attr)
        try:
            self.__setitem__(attr, value)
        except IndexError as error:
            raise AttributeError from error

    def __setitem__(self, attr, value):
        """Set apropriate attribute on data container."""
        self.dct.__setitem__(attr, value)

    def __repr__(self):
        """Representation."""
        return('Objectify({})'.format(self.dct))

    def __bool__(self):
        """Assure truthy value is False when appropriate."""
        return bool(self.dct)


def _accepts_pos_kw(func=None, signature=None):
    """Return a boolean 2-tuple on whether a function accepts *args or **kw."""
    signature = signature or inspect.signature(func)
    parameter_types = {p.kind for p in signature.parameters.values()}
    return (inspect.Parameter.VAR_POSITIONAL in parameter_types,
            inspect.Parameter.VAR_KEYWORD in parameter_types)


def inject_call(func: 'callable', *args: ['any'], **kwargs: {str: 'any'}) -> 'any':
    """Perform a function call, injecting apropriate parameters from kwargs.

    Other parameters are ignored.  (If you want errors on nonexisting parameters
    just call the function directly)

    :param func: the callable
    :param args: positional args to be unconditionally forwarded to the callable
    :param kwargs: keyword parameters that will be filtered to whatever the callable
                   explicitly accepts before being forwarded.
    :return: Whatever the callale returns.
    """
    signature = inspect.signature(func)

    accepts_pos, accepts_kw = _accepts_pos_kw(signature=signature)
    if accepts_kw:
        # Anything goes -
        return func(*args, **kwargs)

    new_kw = {}
    for key, value in kwargs.items():
        if key in signature.parameters:
            new_kw[key] = value
    return func(*args, **new_kw)
