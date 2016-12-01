"""Tests for `briefy.common.vocabularies.roles` module."""
from briefy.common.vocabularies import LabeledEnum


def test_labeled_enums():
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


def test_labeled_enums_with_2_items():
    options = (
        ('food', 'Food'),
        ('interior', 'Interior'),
        ('journalism', 'Journalism/Documentary'),
        ('landscape', 'Landscape'),
    )
    Categories = LabeledEnum('Categories', options)
    assert str(Categories.interior) == 'Categories.interior'
    assert Categories.interior.value == 'interior'
    assert Categories.interior.label == 'Interior'
