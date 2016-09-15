"""Timestamp mixin."""
from briefy.common.db import datetime_utcnow

import sqlalchemy as sa


class Timestamp:
    """A mixin providing timestamp information."""

    created_at = sa.Column(sa.DateTime(), default=datetime_utcnow)
    updated_at = sa.Column(sa.DateTime(), default=datetime_utcnow, onupdate=datetime_utcnow)
