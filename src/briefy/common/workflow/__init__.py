"""Briefy.Workflow."""
from briefy.common.workflow.exceptions import WorkflowException
from briefy.common.workflow.exceptions import WorkflowPermissionException
from briefy.common.workflow.exceptions import WorkflowStateException
from briefy.common.workflow.exceptions import WorkflowTransitionException
from briefy.common.workflow.permission import Permission
from briefy.common.workflow.state import WorkflowState
from briefy.common.workflow.state import WorkflowStateGroup
from briefy.common.workflow.transition import WorkflowTransition
from briefy.common.workflow.workflow import BriefyWorkflow
from briefy.common.workflow.workflow import Workflow
from zope.interface import Attribute
from zope.interface import Interface


permission = Permission

__all__ = (
    'Workflow',
    'BriefyWorkflow',
    'IWorkflow',
    'permission',
    'Permission',
    'WorkflowException',
    'WorkflowPermissionException',
    'WorkflowState',
    'WorkflowStateException',
    'WorkflowStateGroup',
    'WorkflowTransition',
    'WorkflowTransitionException',
)


class IWorkflow(Interface):
    """Interface for a Workflow."""

    entity = Attribute("""Entity name.""")
    name = Attribute("""Workflow name.""")
    initial_state = Attribute("""Initial state for this workflow.""")
    state_key = Attribute("""Key/Attribute to be used to store workflow state.""")
    history_key = Attribute("""Key/Attribute to be used to store workflow history.""")
