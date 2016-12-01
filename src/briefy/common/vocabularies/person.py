"""Personal categories."""
from briefy.common.vocabularies import LabeledEnum


options = [
    ('f', 'f', 'Female'),
    ('m', 'm', 'Male')
]


GenderCategories = LabeledEnum('GenderCategories', options)
