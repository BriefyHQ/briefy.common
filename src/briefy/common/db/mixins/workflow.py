"""Workflow mixin."""
from sqlalchemy.dialects.postgresql import JSONB

import sqlalchemy as sa


class Workflow:
    """A mixin providing workflow information."""

    state = sa.Column(sa.String(100))
    state_history = sa.Column(JSONB())
