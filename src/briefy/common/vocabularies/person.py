"""Personal categories."""
from briefy.common.vocabularies import LabeledEnum


options = [
    ('f', 'f', 'Female'),
    ('m', 'm', 'Male'),
    ('o', 'o', 'Other'),
    ('n', 'n', 'N/A')
]


GenderCategories = LabeledEnum('GenderCategories', options)
