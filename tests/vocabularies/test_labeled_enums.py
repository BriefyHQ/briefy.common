"""Tests for `briefy.common.vocabularies.roles` module."""
from briefy.common.vocabularies import LabeledEnum

import pytest


@pytest.fixture
def options():
    """Enum options fixture."""
    options = (
        ('food', 'Food'),
        ('interior', 'Interior'),
        ('journalism', 'Journalism/Documentary'),
        ('landscape', 'Landscape'),
    )
    return options


def test_labeled_enums():
    """Test labeled enums."""
    options = (
        ('food', 'food', 'Food'),
        ('interior', 'interior', 'Interior'),
        ('journalism', 'journalism', 'Journalism/Documentary'),
        ('landscape', 'landscape', 'Landscape'),
    )
    Categories = LabeledEnum('Categories', options)
    assert str(Categories.interior) == 'Categories.interior'
    assert Categories.interior.value == 'interior'
    assert Categories.interior.label == 'Interior'


def test_labeled_enums_with_2_items(options):
    """Test labeled enums with 2 items."""
    Categories = LabeledEnum('Categories', options)
    assert str(Categories.interior) == 'Categories.interior'
    assert Categories.interior.value == 'interior'
    assert Categories.interior.label == 'Interior'


MCategories = LabeledEnum('MCategories', options())
""" Pickable enums have to be retrievable from the module level."""


def test_labeled_enums_are_pickable():
    """Test labeled enums are pickable."""
    import pickle
    assert pickle.dumps(MCategories.food)
    v = pickle.dumps(MCategories.interior)
    assert pickle.loads(v) is MCategories.interior
