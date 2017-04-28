"""Utility classes and functions to ease the use of colander validators

Warning: This module relies on feature of Python 3.6 and above.

Defines simple readable, compact and expressive way
to create colander SchemaNodes.

This will allow both document and implement complex JSON based
fields - like the ones needed for project delivery configuration
and asset metadata like a Python dict, and still
have all the power of pylons.colander for validation
and serialization of code.


Examples of literal schema declaration:


schema = MK({
    "name": C.string | C.nullable | C.default(None),
    "metadata": {
        "_": C.dict| C.mandatory
    }
})
"""

import colander
import sys


class V:
    """Namespace to shortcut colander validatoes"""

    email = colander.Email
    one_of = colander.OneOf
    length = colander.Length


class _NameSpace:
    """Namespace object able to be used in dicts and sets."""
    def __new__(cls, *args, **kw):
        """__new__  because we are not supposed to have the keys modified after creation."""
        self = object.__new__(cls)
        # From what is new in Python 3.6:
        # The order of elements in **kwargs now corresponds to the order
        # in which keyword arguments were passed to the function.
        self._order = tuple(kw.keys())
        self.__dict__.update(kw)
        return self

    def __setattr__(self, attr, value):
        """Check if attr can actually be set"""
        if attr.startswith('_') or attr in self.__dict__:
            super().__setattr__(attr, value)
            return
        raise AttributeError(f"NameSpace object has no attribute '{attr}'")

    def __call__(self, *args, **kw):
        """Sets contained parameters."""
        seem = set()
        for attr, arg in zip(self._order, args):
            setattr(self, attr, arg)
            seem.add(attr)
        for attr, arg in kw.items():
            if attr in seem:
                raise AttributeError(
                    f'Attempt to set "{attr}"  as both positional and keyword parameter')
            setattr(self, attr, arg)
        return self

    # Default __eq__ implementation (== 'is') is enough for us.

    def __repr__(self):
        """repr"""
        return f'_NameSpace(**{self.__dict__})'

    def __hash__(self):
        """hash"""
        return hash(''.join(self.__dict__.keys()))


class SchemaParameters:
    """Container class creating magic schema field attributes."""
    bool = colander.Bool
    int = colander.Int
    string = colander.String
    date = colander.Date
    timestamp = colander.DateTime

    uuid = "uuid"
    missing = "missing"
    t = _NameSpace(title='')
    v = _NameSpace(validator=None)

    def __init__(self, *args):
        self._parameters = set(args)

    def __getattribute__(self, attr):
        """Set the magic attribute as 'used' for this class.
        :return: self
        """
        if attr.startswith('_'):
            return super().__getattribute__(attr)
        if attr in self.__class__.__dict__:
            value = getattr(__class__, attr)
            if isinstance(value, _NameSpace):
                # Allows the attribute to be called to set its values, and lazily returns self
                value = lambda *args, **kw: (value(*args, **kw), self)[1]
            result = self.__class__()
            result._parameters.add(value)
            return result

    def __or__(self, other):
        result = self.__class__()
        result._parameters = self._parameters.copy()
        result._parameters.update(other._parameters)
        return result

    def __repr__(self):
        return f'SchemaParameters(*self._parameters))'


C = SchemaParameters()


def make_schema(schema, parent=None):
    if isinstance(schema, dict):
        result = colander.MappingSchema())
    for key, value in schema.items():
        if isinstance(value, C):
            node = colander.SchemaNode(**value._parameters)
        result.add(node)
    return result





MK = make_schema
