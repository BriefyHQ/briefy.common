"""Briefy base workflow."""
from .base import Workflow
from .base import WorkflowTransition
from briefy.common.event.workflow import WorkflowTransitionEvent
from zope.event import notify

import logging

logger = logging.getLogger(__name__)


class BriefyWorkflow(Workflow):
    """Workflow for an object on Briefy."""

    entity = ''
    """Entity this workflow manages."""

    state_key = 'state'
    """Attribute, on the object, to store Workflow state."""

    history_key = 'state_history'
    """Attribute, on the object, to store Workflow history."""

    context_key = 'workflow_context'
    """Attribute storing workflow context (User)."""

    @property
    def name(self) -> str:
        """Return the name of this workflow."""
        return '{entity}.workflow'.format(entity=self.entity)

    def _notify(self, transition: WorkflowTransition) -> None:
        """Notify when a WorkflowTransition is executed.

        Trigger a :class:`briefy.common.event.workflow.WorkflowTransitionEvent` event.
        """
        obj = self.document
        history = self.history
        entry = history[-1] if history else {}
        logger.info(
            'Transition {name} was executed for object {obj}'.format(
                name=transition.title,
                obj=str(obj),
            ),
            extra={'history_entry': entry}
        )
        request = None
        if hasattr(obj, 'request'):
            request = obj.request
        user = self.context
        # Fire event
        wf_transition_event = WorkflowTransitionEvent(
            self.document, request, transition, user
        )
        # Notify using zope.event
        notify(wf_transition_event)

        wf_transition_event()
        super()._notify(transition)
