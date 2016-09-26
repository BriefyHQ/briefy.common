"""Workflow mixin."""
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy_utils import JSONType

import colander
import sqlalchemy as sa


class WorkflowBase:
    """A mixin providing workflow information."""

    _workflow = None

    # These 3 variables in the model will keep the workflow state
    # during the model lifecycle.
    # Attempt that the "_workflow_context" will usually contain
    # information about the user for the current request, and is
    # not persisted or serialized
    _workflow_context = None
    state = ''
    state_history = None

    def __init__(self, *args, workflow_context=None, **kwargs):
        """Initialize object workflow.

        Otherwise its initial state is not set.
        """
        self.workflow_context = workflow_context
        self.workflow  # noqa
        return super().__init__(*args, **kwargs)

    @property
    def workflow(self):
        """Return the workflow applied to this document."""
        workflow = self._workflow
        if workflow:
            return workflow(self)

    @property
    def workflow_context(self):
        """Return the workflow context (user) applied to this document."""
        return self._workflow_context

    @workflow_context.setter
    def workflow_context(self, value):
        """Set the workflow context (user) to this document."""
        self._workflow_context = value


class Workflow(WorkflowBase):
    """A mixin providing workflow information, SQLALChemy aware."""

    _workflow = None

    state = sa.Column(sa.String(100))
    _state_history = sa.Column('state_history',
                               JSONType,
                               info={'colanderalchemy': {
                                   'title': 'State history',
                                   'missing': colander.drop,
                                   'typ': colander.String}}
                               )

    @property
    def state_history(self):
        """State history property getter."""
        return self._state_history

    @state_history.setter
    def state_history(self, value):
        """State history property setter."""
        self._state_history = value
        flag_modified(self, '_state_history')

    def to_dict(self, *args, **kwargs):
        """Return a dictionary with fields and values used by this Class."""
        data = super().to_dict(*args, **kwargs)
        data['state_history'] = self.state_history
        return data
