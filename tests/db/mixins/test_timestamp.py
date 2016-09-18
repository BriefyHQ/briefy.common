"""Test Timestamp mix."""
from briefy.common.db import Base
from briefy.common.db.mixins import Mixin
from conftest import DBSession
from datetime import datetime
from pytz import timezone
from pytz import utc

import pytest


class TimestampExample(Mixin, Base):
    """A Timestamp example."""

    __tablename__ = 'tz_examples'
    __session__ = DBSession


@pytest.mark.usefixtures("db_transaction")
class TestTimestamp:
    """Test Timestamp database model."""

    def test_mixin(self, session):
        """Test mixin behavior."""
        # Send datetime as not naive, with timezone
        berlin = timezone('Europe/Berlin')
        created_at = berlin.localize(datetime(2016, 12, 12, 12, 12, 12))

        example_data = {
            'id': '6b6f0b2a-25ed-401c-8c65-3d4009e398ea',
            'created_at': created_at,
            'updated_at': created_at,
        }
        example = TimestampExample(**example_data)
        session.add(example)
        session.commit()
        session.flush()
        example = session.query(TimestampExample).first()

        assert isinstance(example, TimestampExample)
        assert example.created_at == datetime(2016, 12, 12, 11, 12, 12, tzinfo=utc)
