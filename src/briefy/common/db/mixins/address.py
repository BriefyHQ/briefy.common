"""Address mixin."""
from geoalchemy2 import Geometry
from sqlalchemy_utils import CountryType, JSONType

import sqlalchemy as sa


class Address:
    """Base address information."""

    city = sa.Column(sa.String(255), nullable=False)
    info = sa.Column(JSONType)
    country = sa.Column(CountryType, nullable=False)
    coordinates = sa.Column(Geometry('POINT'))
