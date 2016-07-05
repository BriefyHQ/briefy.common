"""Workflow mixin."""
from sqlalchemy.dialects.postgresql import JSONB

import sqlalchemy as sa


class Workflow:
    """A mixin providing workflow information."""

    _workflow = None

    state = sa.Column(sa.String(100), default='created')
    state_history = sa.Column(JSONB())

    @property
    def workflow(self):
        """Return the workflow applied to this class."""
        workflow = self._workflow
        if workflow:
            return workflow(self)
