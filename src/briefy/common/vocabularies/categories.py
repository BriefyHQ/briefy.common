"""Job categories."""
from enum import Enum


class CategoryChoices(Enum):
    """Categories available for jobs and professionals."""

    undefined = 'undefined'
    three_sixty = '360 Degree'
    accommodation = 'Accommodation'
    aerial = 'Aerial'
    architecture = 'Architecture'
    nude = 'Boudoir/Nude'
    car = 'Car'
    child = 'Child/Newborn'
    city = 'City'
    company = 'Company'
    event = 'Event'
    fashion = 'Fashion'
    food = 'Food'
    interior = 'Interior'
    journalism = 'Journalism/Documentary'
    landscape = 'Landscape'
    lifestype = 'Lifestyle'
    macro = 'Macro'
    misc = 'Miscellaneous'
    nature = 'Nature'
    portrait = 'Portrait'
    product = 'Product'
    real_state = 'Real Estate'
    restaurant = 'Restaurant'
    sports = 'Sports'
    video = 'Video'
    wedding = 'Wedding'
