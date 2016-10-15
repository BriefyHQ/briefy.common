"""Briefy base workflow."""
from .base import Workflow
from briefy.common.event.workflow import WorkflowTranstionEvent
import logging

logger = logging.getLogger(__name__)


class BriefyWorkflow(Workflow):
    """Workflow for an object on Briefy."""

    entity = ''
    state_key = 'state'
    history_key = 'state_history'
    context_key = 'workflow_context'

    @property
    def name(self):
        """Return the name of this workflow."""
        return '{}.workflow'.format(self.entity)

    def _notify(self, transition):
        """Notify when a transition happens."""
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
        user = self.context
        # Fire event
        wf_transition_event = WorkflowTranstionEvent(
            self.document, request, transition, user
        )
        wf_transition_event()
        super()._notify(transition)
