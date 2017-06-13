"""Workflow support for Briefy objects."""
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy_utils import JSONType

import colander
import sqlalchemy as sa


class WorkflowBase:
    """A mixin providing workflow support."""

    _workflow = None
    """Workflow to be used.

    This will be overwritten in subclasses.
    """

    _workflow_context = None
    """Context will usually contain information about the user for the current request.

    This info is not persisted.
    """

    state = ''
    """Workflow state id."""

    request = None
    """Point to the current web app request when available."""

    state_history = None
    """Workflow history.

    List with all transitions for this object.
    """

    def __init__(self, *args, workflow_context=None, request=None, **kwargs):
        """Initialize object workflow.

        Otherwise its initial state is not set.
        """
        self.request = request
        self._workflow_context = workflow_context
        _ = self.workflow  # noqa
        super().__init__(*args, **kwargs)

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
    """A mixin providing workflow information, SQLAlchemy aware."""

    state = sa.Column(sa.String(100))
    """Workflow state id."""

    _state_history = sa.Column(
        'state_history',
        JSONType,
        info={
            'colanderalchemy': {
                'title': 'State history',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Workflow history.

    List with all transitions for this object.
    """

    @property
    def state_history(self):
        """State history property getter."""
        return self._state_history

    @state_history.setter
    def state_history(self, value):
        """State history property setter."""
        self._state_history = value
        flag_modified(self, '_state_history')

    def to_dict(self, *args, **kwargs) -> dict:
        """Return a dictionary with fields and values used by this Class."""
        data = {}
        includes = kwargs.get('includes', [])
        if includes and 'state_history' in includes:
            kwargs['includes'] = kwargs['includes'][:]
            kwargs['includes'].remove('state_history')
            data['state_history'] = self.state_history
        data.update(super().to_dict(*args, **kwargs))
        return data
