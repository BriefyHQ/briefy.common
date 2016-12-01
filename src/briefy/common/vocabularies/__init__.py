"""Vocabularies used by Briefy systems."""
from enum import Enum
import sys


def LabeledEnum(class_name: str, names: list) -> Enum:
    """
    Utility to build Enum's where all items have a non-optional 'label' attribute

    :param class_name: The name of the enum
    :param names: A sequence where each item is a 3-item sequence with ('name', 'value', 'label')
                  or a two-item seq. where each item is ('name', 'label') and name is doubled as value.

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
    new_enum = Enum(class_name, names=enum_names, module=module, qualname=qualname)
    for enum_item, item in zip(new_enum, names):
        enum_item.label = item[label_index]
    return new_enum
