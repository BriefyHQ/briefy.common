"""Briefy base workflow."""
from .base import Workflow

import logging

logger = logging.getLogger(__name__)


class BriefyWorkflow(Workflow):
    """Workflow for an object on Briefy."""

    entity = ''
    state_key = 'state'
    history_key = 'state_history'
    context_key = '_workflow_context'

    @property
    def name(self):
        """Return the name of this workflow."""
        return '{}.workflow'.format(self.entity)

    def _notify(self, transition):
        """Notify when a transition happens."""
        history = self.history
        entry = history[-1] if history else {}
        logger.info(
            'Transition {name} was executed for object {obj}'.format(
                name=transition.title,
                obj=str(self.document),
            ),
            extra={'history_entry': entry}
        )
        super()._notify(transition)
