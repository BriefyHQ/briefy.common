"""Job categories."""
from briefy.common.vocabularies import LabeledEnum


options = [
    ('undefined', 'undefined', 'undefined'),
    ('three_sixty', 'three_sixty', '360 Degree'),
    ('accommodation', 'accommodation', 'Accommodation'),
    ('aerial', 'aerial', 'Aerial'),
    ('architecture', 'architecture', 'Architecture'),
    ('nude', 'nude', 'Boudoir/Nude'),
    ('car', 'car', 'Car'),
    ('child', 'child', 'Child/Newborn'),
    ('city', 'city', 'City'),
    ('company', 'company', 'Company'),
    ('event', 'event', 'Event'),
    ('fashion', 'fashion', 'Fashion'),
    ('food', 'food', 'Food'),
    ('interior', 'interior', 'Interior'),
    ('journalism', 'journalism', 'Journalism/Documentary'),
    ('landscape', 'landscape', 'Landscape'),
    ('lifestype', 'lifestype', 'Lifestyle'),
    ('macro', 'macro', 'Macro'),
    ('misc', 'misc', 'Miscellaneous'),
    ('nature', 'nature', 'Nature'),
    ('portrait', 'portrait', 'Portrait'),
    ('product', 'product', 'Product'),
    ('real_state', 'real_state', 'Real Estate'),
    ('restaurant', 'restaurant', 'Restaurant'),
    ('sports', 'sports', 'Sports'),
    ('video', 'video', 'Video'),
    ('wedding', 'wedding', 'Wedding'),
]


CategoryChoices = LabeledEnum('CategoryChoices', options)

PhotoCategoryChoices = LabeledEnum('PhotoCategoryChoices', options)

VideoCategoryChoices = LabeledEnum('VideoCategoryChoices', options)
