"""Address mixin."""
from briefy.common.db.types.geo import POINT
from sqlalchemy_utils import TimezoneType
from sqlalchemy.orm import object_session


import colander
import json
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class Address:
    """Base address information.

    This mixin provides the base interface for an Address.
    Design decision was to require at least the following fields:

        * locality: City/Town of this address
        * country: ISO 3166 representation of a Country.

    Additionally we have a field called info that stores a dict with more detailed information.
    """

    country = sa.Column(sautils.CountryType, nullable=False)
    """Country of this adddress.

    Country will be stored as a ISO 3166-2 information.
    i.e.: DE, BR, ID
    """

    locality = sa.Column(sa.String(255), nullable=False)
    """Locality of this adddress.

    Locality could be a City, a Town or similar.
    i.e.: Bangkok, Berlin, São Paulo
    """

    info = sa.Column(sautils.JSONType)
    """Structure containing address information.

    Info expected schema::

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

    timezone = sa.Column(TimezoneType(backend='pytz'), default='UTC')
    """Timezone in which this address is located.

    i.e.: UTC, Europe/Berlin
    """

    _coordinates = sa.Column(
        'coordinates',
        POINT,
        info={
            'colanderalchemy': {
                'title': 'Geo JSON Point coordinates',
                'typ': colander.Mapping
            }
        }
    )
    """Attribute to store the coordinates (lat, lng) for this object.

    Should always be accessed using :func:`Address.coordinates` property.
    """

    @property
    def coordinates(self) -> dict:
        """Return coordinates as a GeoJSON object.

         For a Point it is like:

            'coordinates': {
                'type': 'Point',
                'coordinates': [52.4994805, 13.4491646]
            },


        :returns: Coordinates as a GeoJSON object
        """
        coordinates = self._coordinates
        session = object_session(self)
        if session:
            return json.loads(
                session.scalar(coordinates.ST_AsGeoJSON())
            )

    @coordinates.setter
    def coordinates(self, value: dict):
        """Set coordinates from a GeoJSON.

        :param value: Dictionary containing a GeoJSON object
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
