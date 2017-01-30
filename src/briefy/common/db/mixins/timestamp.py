"""Timestamp mixin."""
from briefy.common.config import IMPORT_KNACK
from briefy.common.db import datetime_utcnow
from briefy.common.db.types import AwareDateTime
from sqlalchemy.ext.declarative import declared_attr

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

    @declared_attr
    def updated_at(cls):
        """Last update date of this object.

        Returns a datetime object, always in UTC, representing when this object was last updated.
        """
        kwargs = dict(default=datetime_utcnow)
        if not IMPORT_KNACK:
            kwargs.update(onupdate=datetime_utcnow)
        return sa.Column(
            AwareDateTime(),
            **kwargs,
        )
