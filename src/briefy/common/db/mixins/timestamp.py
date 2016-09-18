"""Timestamp mixin."""
from briefy.common.db import datetime_utcnow
from briefy.common.db.types.aware_datatime import AwareDateTime

import sqlalchemy as sa


class Timestamp:
    """A mixin providing timestamp information."""

    created_at = sa.Column(AwareDateTime(), default=datetime_utcnow)
    updated_at = sa.Column(AwareDateTime(), default=datetime_utcnow, onupdate=datetime_utcnow)
