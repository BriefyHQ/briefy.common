"""Address mixin."""
from briefy.common.db.types.geo import POINT
from sqlalchemy_utils import CountryType, JSONType
from sqlalchemy.orm import object_session

import json
import sqlalchemy as sa


class Address:
    """Base address information."""

    locality = sa.Column(sa.String(255), nullable=False)
    info = sa.Column(JSONType)
    country = sa.Column(CountryType, nullable=False)
    _coordinates = sa.Column('coordinates', POINT)

    @property
    def coordinates(self):
        """Return coordinates as a GeoJSON object.

        :returns: Coordinates as a GeoJSON object
        :rtype: dict
        """
        coordinates = self._coordinates
        session = object_session(self)
        if session:
            return json.loads(
                session.scalar(coordinates.ST_AsGeoJSON())
            )

    @coordinates.setter
    def coordinates(self, value):
        """Set coordinates from a GeoJSON.

        :param value: Dictionary containing a GeoJSON object
        :type value: dict
        """
        value = json.dumps(value)
        self._coordinates = value

    @property
    def latlng(self):
        """Return coordinates as a tuple.

        :returns: A tuple containing latitude and longitude
        :rtype: tuple
        """
        coordinates = self.coordinates
        point = coordinates.get('coordinates', None)
        if point:
            return tuple(point)
