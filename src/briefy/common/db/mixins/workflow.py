"""Workflow mixin."""
from sqlalchemy_utils import JSONType

import sqlalchemy as sa


class WorkflowBase:
    """A mixin providing workflow information."""

    _workflow = None

    state = ''
    state_history = None

    def __init__(self, *args, **kwargs):
        """Initialize object workflow.

        Otherwise its initial state is not set.
        """
        self.workflow  # noqa
        return super().__init__(*args, **kwargs)

    @property
    def workflow(self):
        """Return the workflow applied to this document."""
        workflow = self._workflow
        if workflow:
            return workflow(self)


class Workflow(WorkflowBase):
    """A mixin providing workflow information, SQLALChemy aware."""

    _workflow = None

    state = sa.Column(sa.String(100))
    state_history = sa.Column(JSONType)
