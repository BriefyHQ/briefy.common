"""Test AddressMixin model."""
from briefy.common.db import Base
from briefy.common.db.mixins import AddressMixin
from conftest import DBSession
from pytz import timezone

import pytest


location_data = {
    'updated_at': '2016-09-08T15:36:28.087123Z',
    'locality': 'Berlin',
    'country': 'DE',
    'formatted_address': 'Schlesische Straße 27, Kreuzberg, Berlin, 10997, DE',
    'coordinates': {
        'type': 'Point',
        'coordinates': [52.4994805, 13.4491646]
    },
    'info': {
        'additional_info': 'House 3, Entry C, 1st. floor, c/o GLG',
        'formatted_address': 'Schlesische Straße 27, Kreuzberg, Berlin, 10997, DE',
        'province': 'Berlin',
        'locality': 'Berlin',
        'sublocality': 'Kreuzberg',
        'route': 'Schlesische Straße',
        'street_number': '27',
        'country': 'DE',
        'postal_code': '10997'
    },
    'timezone': 'Europe/Berlin',
    'id': '6b6f0b2a-25ed-401c-8c65-3d4009e398ea',
    'created_at': '2016-09-08T15:36:28.087112Z'
}


class Location(AddressMixin, Base):
    """A Location."""

    __tablename__ = 'locations'
    __session__ = DBSession


@pytest.mark.usefixtures('db_transaction')
class TestAddressMixin:
    """Test Professional database model."""

    def test_create_location(self, session):
        """Create a location instance."""
        location = Location(**location_data)
        session.add(location)
        session.commit()
        session.flush()
        location = session.query(Location).first()

        assert isinstance(location, Location)

        assert isinstance(location.coordinates, dict)

        assert isinstance(location.latlng, tuple)

        assert location.timezone == timezone('Europe/Berlin')
