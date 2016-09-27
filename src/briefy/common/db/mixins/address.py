"""Address mixin."""
from briefy.common.db.types.geo import POINT
from sqlalchemy_utils import TimezoneType
from sqlalchemy.orm import object_session


import colander
import json
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class Address:
    """Base address information."""

    locality = sa.Column(sa.String(255), nullable=False)
    """
    Info expected schema:
    {
      'additional_info': 'House 3, Entry C, 1st. floor, c/o GLG',
      'province': 'Berlin',
      'locality': 'Berlin',
      'sublocality': 'Kreuzberg',
      'route': 'Schlesische Straße',
      'street_number': '27',
      'country': 'DE',
      'postal_code': '10997'
    },
    """
    info = sa.Column(sautils.JSONType)
    country = sa.Column(sautils.CountryType, nullable=False)
    _coordinates = sa.Column('coordinates', POINT,
                             info={'colanderalchemy': {
                                 'title': 'Geo JSON Point coordinates',
                                 'typ': colander.Mapping,
                             }})

    timezone = sa.Column(TimezoneType(backend='pytz'), default='UTC')

    @property
    def coordinates(self):
        """Return coordinates as a GeoJSON object.

         For a Point it is like:

            'coordinates': {
                'type': 'Point',
                'coordinates': [52.4994805, 13.4491646]
            },


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

    # TODO: create a latlng setter!
