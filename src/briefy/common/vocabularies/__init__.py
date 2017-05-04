"""Vocabularies used by Briefy systems."""
from enum import Enum
from importlib import import_module

import sys


# Due to being defined out of their native '__module__', these labeled enums
# were not able to be pickled or unpickled (even with __module__ an __qualname__
# being explicitly set).
# This subclass and helper function override pickle's behavior for our Enums
# so that they work.


def _safe_pickle_load(module_name, class_name, item_name):
    """Called by pickle.load with information to retrieve an Enum item."""
    module = import_module(module_name)
    enum_class = getattr(module, class_name)
    return getattr(enum_class, item_name)


class SafePickeableEnum(Enum):
    """Safely pickleable version of Enum."""

    def __reduce_ex__(self, protocol):
        """Return the callable and parameters needed to unpickle an Enum item."""
        return (_safe_pickle_load, (self.__module__, self.__class__.__name__, self.name))


def LabeledEnum(class_name: str, names: list) -> Enum:
    """
    Utility to build Enum's where all items have a non-optional 'label' attribute.

    :param class_name: The name of the enum
    :param names: A sequence where each item is a 3-item sequence with ('name', 'value', 'label')
                  or a two-item seq. where each item is ('name', 'label')
                  and name is doubled as value.

    """
    original_frame = sys._getframe().f_back
    module = original_frame.f_globals['__name__']
    qualname = '.'.join((module, class_name))
    if len(names[0]) == 3:
        enum_names = [item[:2] for item in names]
        label_index = 2
    else:
        enum_names = [(item[0], item[0]) for item in names]
        label_index = 1
    new_enum = SafePickeableEnum(class_name, names=enum_names, module=module, qualname=qualname)
    for enum_item, item in zip(new_enum, names):
        enum_item.label = item[label_index]
    return new_enum
