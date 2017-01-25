"""Timestamp mixin."""
from briefy.common.db import datetime_utcnow
from briefy.common.db.types import AwareDateTime

import sqlalchemy as sa


class Timestamp:
    """A mixin providing timestamp information.

    This is used to track object creation and updates.
    """

    created_at = sa.Column(
        AwareDateTime(),
        default=datetime_utcnow
    )
    """Creation date of this object.

    Returns a datetime object, always in UTC, representing when this object was created.
    """

    updated_at = sa.Column(
        AwareDateTime(),
        default=datetime_utcnow,
        # TODO: return this after migration
        # onupdate=datetime_utcnow
    )
    """Last update date of this object.

    Returns a datetime object, always in UTC, representing when this object was last updated.
    """
