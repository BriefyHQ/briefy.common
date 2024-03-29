"""Address mixin."""
from briefy.common.db.types.geo import POINT
from briefy.common.utils import schema
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import object_session
from sqlalchemy_utils import TimezoneType

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

    country = sa.Column(sautils.CountryType, index=True, nullable=False)
    """Country of this address.

    Country will be stored as a ISO 3166-2 information.
    i.e.: DE, BR, ID
    """

    locality = sa.Column(sa.String(255), index=True, nullable=False)
    """Locality of this address.

    Locality could be a City, a Town or similar.
    i.e.: Bangkok, Berlin, São Paulo
    """

    formatted_address = sa.Column(sa.String(255), nullable=True)
    """Address to be displayed on the user interface.

    We use this as a fail safe against problems in the geocoding.
    i.e.: Schlesische Straße 27, Kreuzberg, Berlin, 10997, DE
    """

    info = sa.Column(
        JSONB,
        info={
            'colanderalchemy': {
                'typ': schema.JSONType
            }
        }
    )
    """Structure containing address information.

    Info expected schema::

        {
          'additional_info': 'House 3, Entry C, 1st. floor, c/o GLG',
          'formatted_address': 'Schlesische Straße 27, Kreuzberg, Berlin, 10997, DE',
          'place_id': 'ChIJ8-exwVNOqEcR8hBPr-VUmdQ',
          'province': 'Berlin',
          'locality': 'Berlin',
          'sublocality': 'Kreuzberg',
          'route': 'Schlesische Straße',
          'street_number': '27',
          'country': 'DE',
          'postal_code': '10997'
        }

    Ref: https://maps-apis.googleblog.com/2016/11/address-geocoding-in-google-maps-apis.html
    """

    timezone = sa.Column(TimezoneType(backend='pytz'), default='UTC')
    """Timezone in which this address is located.

    i.e.: UTC, Europe/Berlin
    """

    _coordinates = sa.Column(
        'coordinates',
        POINT,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Geo JSON Point coordinates',
                'typ': schema.Coordinate,
                'missing': colander.drop,
            }
        }
    )
    """Attribute to store the coordinates (lat, lng) for this object.

    Should always be accessed using :func:`Address.coordinates` property.
    """

    @hybrid_property
    def coordinates(self) -> dict:
        """Return coordinates as a GeoJSON object.

         For a Point it is like::

            'coordinates': {
                'type': 'Point',
                'coordinates': [52.4994805, 13.4491646]
            },

        :returns: Coordinates as a GeoJSON object
        """
        coordinates = self._coordinates
        if not isinstance(coordinates, str):
            session = object_session(self)
            if session:
                if coordinates is not None:
                    coordinates = session.scalar(coordinates.ST_AsGeoJSON())
                else:
                    return
        return json.loads(coordinates)

    @coordinates.setter
    def coordinates(self, value: dict):
        """Set coordinates from a GeoJSON.

        :param value: Dictionary containing a GeoJSON object
        """
        if isinstance(value, (list, tuple)):
            # We assume is (lat, lng)
            # so, to deal with GeoJSON, we swap it
            value = {
                'type': 'Point',
                'coordinates': [value[1], value[0]]
            }

        # this should keep only for the model tests
        elif isinstance(value, dict):
            if isinstance(value['coordinates'][0], str):
                return

        value = json.dumps(value)
        self._coordinates = value

    @coordinates.expression
    def coordinates(cls):
        """Expression to be used on gis queries."""
        return cls._coordinates

    @hybrid_method
    def distance(self, value=(0.0, 0.0)):
        """Distance between this address and another location."""
        if self.coordinates:
            return sa.func.ST_Distance(self.coordinates, sa.func.ST_MakePoint(*value), True)

    @hybrid_property
    def latlng(self):
        """Return coordinates as a tuple.

        :returns: A tuple containing latitude and longitude
        :rtype: tuple
        """
        coordinates = self.coordinates
        point = coordinates.get('coordinates', None) if coordinates else None
        if point:
            lng, lat = point
            return lat, lng
