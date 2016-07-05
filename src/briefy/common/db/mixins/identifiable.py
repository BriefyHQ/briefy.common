"""Identifiable mixin."""
from briefy.common.utils.data import generate_uuid

import sqlalchemy as sa


class GUID:
    """A Mixin providing a id as primary key."""

    id = sa.Column(sa.CHAR(36), unique=True, primary_key=True, default=generate_uuid)
