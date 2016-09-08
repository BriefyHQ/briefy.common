"""Briefy.Workflow."""
from .base import Permission
from .base import permission
from .base import WorkflowState
from .base import WorkflowStateGroup
from .base import WorkflowTransition
from .exceptions import WorkflowException
from .exceptions import WorkflowPermissionException
from .exceptions import WorkflowStateException
from .exceptions import WorkflowTransitionException
from .workflow import BriefyWorkflow
from zope.interface import Attribute
from zope.interface import Interface


__all__ = [
    'permission',
    'Permission',
    'BriefyWorkflow',
    'IWorkflow',
    'WorkflowException',
    'WorkflowPermissionException',
    'WorkflowState',
    'WorkflowStateException',
    'WorkflowStateGroup',
    'WorkflowTransition',
    'WorkflowTransitionException',
]


class IWorkflow(Interface):
    """Interface for a Workflow."""

    entity = Attribute("""Entity name.""")
    name = Attribute("""Workflow name.""")
    initial_state = Attribute("""Initial state for this workflow.""")
    state_key = Attribute("""Key/Attribute to be used to store workflow state.""")
    history_key = Attribute("""Key/Attribute to be used to store workflow history.""")
