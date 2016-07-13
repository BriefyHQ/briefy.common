"""Timestamp mixin."""
from datetime import datetime

import sqlalchemy as sa


class Timestamp:
    """A mixin providing timestamp information."""

    created_at = sa.Column(sa.DateTime(), default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
