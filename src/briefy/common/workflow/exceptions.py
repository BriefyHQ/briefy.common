"""Workflow exceptions."""


class WorkflowException(Exception):
    """Workflow Exception."""


class WorkflowStateException(WorkflowException):
    """WorkflowState Exception."""


class WorkflowTransitionException(WorkflowException):
    """WorkflowTransition Exception."""


class WorkflowPermissionException(WorkflowException):
    """WorkflowPermission Exception."""
