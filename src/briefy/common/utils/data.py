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


objectify_sentinel = object()


class Objectify:
    """Alows using values of nested JSON-like data structures as Python objects.

    Helper class to make SQS and HTTP payloads easy to use without
    going too full model declaration. Works great for JSON and
    JSON like objects - avoiding a lot of extraneous
    brackets and quotes for attribute access.

    This works by wrapping a Dictionary or List in Python with
    a  `__getattr__` call, which recursively builds more objects
    of this class if attributes retrieved are also dict or lists.

    List members work as attributes with a `_` prepending their index number.

    If the data structure is needed at any point, it is always available
    at the "_dct" parameter.

    Normally, on trying to retrieve any non-existing attribute, one will get
    an AttributeError - although setting the instance "_sentinel" attribute
    to any object, will return that object on attribute access error instead.

    """


    def __init__(self, dct: (dict, list), sentinel=objectify_sentinel):
        """Initalizer.
        :param dct: Container JSON-Like object to be used.
        """
        # DEPRECATED: Remove '.dct' and leave '._dct' as soon
        # as there are no other references to '.dct' on users of this helper.
        if isinstance(dct, Objectify):
            dct = dct._dct
        self._dct = self.dct = dct
        self._sentinel = sentinel

    def _acceptable_attr(self, attr):
        # DEPRECATED: Remove 'dct' from next verification soon.
        if attr == 'dct' or (attr.startswith('_') and not attr.strip('_').isdigit()):
            return False
        return True

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
        result = self._dct.__getitem__(attr)
        if isinstance(result, (dict, list)):
            return Objectify(result, self._sentinel)
        return result

    def __getattr__(self, attr):
        """Retrieve attribute from underliying object."""
        attr = self._normalize_attr(attr)
        try:
            return self.__getitem__(attr)
        except (KeyError, IndexError, TypeError) as error:
            if self._sentinel is not objectify_sentinel:
                return self._sentinel
            raise AttributeError from error

    def __setattr__(self, attr, value):
        """Set apropriate attribute on underlying object."""
        if not self._acceptable_attr(attr):
            return super().__setattr__(attr, value)
        attr = self._normalize_attr(attr)
        try:
            self.__setitem__(attr, value)
        except IndexError as error:
            raise AttributeError from error

    def __setitem__(self, attr, value):
        """Set apropriate attribute on data container."""
        self._dct.__setitem__(attr, value)

    def __iter__(self):
        """Allows one to iterate over the members of this object.
        Note that this by itself makes these objects  better than JS
        objects due to iterating over data members, and no need to check "hasOwnProperty".

        """
        items = self._dct if isinstance(self._dct, list) else self._dct.values()
        for item in items:
            yield Objectify(item, self._sentinel) if isinstance(item, (dict, list)) else item

    def __dir__(self):
        keys = (
            list(self._dct.keys())
            if isinstance(self._dct, dict) else
            ['_{0}'.format(index) for index in range(len(self._dct))  ]
        )
        return ['_dct', '_sentinel'] + keys

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

