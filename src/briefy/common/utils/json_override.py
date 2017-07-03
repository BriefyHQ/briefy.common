"""Override default JSON dump behavior.

Note that briefy.ws already makes use of Pyramid
internals to use local JSON overrides on all
HTTP JSON serializaton.

That has no effect when we need the custom serializaton
to be used in SQLAlchemy, or used by default
in other parts of the code.

"""

from briefy.common.utils.transformers import to_serializable
from functools import wraps
from json.encoder import JSONEncoder


def new_default(func):
    """Decorator to explicitly override json.encoder.JSONEncoder.default method."""
    @wraps(func)
    def wrapper(self, value):
        try:
            return to_serializable(value)
        except TypeError:
            # Should just raise another typerror -
            # but it is the recomended way of using stdlib.json's encoder
            return func(value)
    return wrapper


def init():
    """Monkey patch 'JSONEncoder.default' method."""
    wrapper = new_default(JSONEncoder.default)
    JSONEncoder.default = wrapper
