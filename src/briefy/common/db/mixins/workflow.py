"""Workflow mixin."""
from sqlalchemy_utils import JSONType

import sqlalchemy as sa


class Workflow:
    """A mixin providing workflow information."""

    _workflow = None

    state = sa.Column(sa.String(100))
    state_history = sa.Column(JSONType)

    def __init__(self, *args, **kwargs):
        # Initializes object workflow.
        # Otherwise its initial state is not set.
        self.workflow  # noqa
        return super().__init__(*args, **kwargs)

    @property
    def workflow(self):
        """Return the workflow applied to this document."""
        workflow = self._workflow
        if workflow:
            return workflow(self)
