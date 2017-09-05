"""Briefy workflow events."""
from briefy import common  # noQA
from briefy.common.event import BaseEvent
from briefy.common.event import IDataEvent
from briefy.common.event import logger
from zope.interface import implementer


class IWorkflowTransitionEvent(IDataEvent):
    """IDataEvent interface for a workflow transition in a workflow."""


@implementer(IWorkflowTransitionEvent)
class WorkflowTransitionEvent(BaseEvent):
    """Base class for workflow transition events.

    This event will write to the events queue on AWS SQS.
    """

    logger = logger

    @property
    def event_name(self) -> str:
        """Automatic generate event name from model class name and transaction name.

        :returns: Event name.
        """
        model_name = self.obj.__class__.__name__.lower()
        transition_name = self.transition.name
        return f'{model_name}.workflow.{transition_name}'

    def __init__(
            self,
            obj: 'common.db.model.Base',
            request,
            transition: 'common.workflow.base.WorkflowTransition',
            user: 'common.types.BaseUser'=None
    ):
        """Custom init to call parent BaseEvent if it exist."""
        self.transition = transition
        self.request = request
        self.obj = obj
        if not user:
            user = getattr(request, 'user', None)
        if user:
            user_id = user.id
        else:
            user_id = None
        kwargs = {'actor': user_id, 'request_id': None}
        super().__init__(obj, **kwargs)

    def __call__(self) -> str:
        """Notify about the event.

        :returns: Id from message in the queue
        """
        obj = self.obj
        logger = self.logger
        queue = self.queue
        payload = {
            'event_name': self.event_name,
            'actor': self.actor,
            'guid': self.guid,
            'created_at': self.created_at,
            'request_id': self.request_id,
            'data': obj.to_dict(includes=['state_history']),
            'transition': self.transition.name,
        }
        message_id = ''
        try:
            message_id = queue.write_message(payload)
        except Exception as exc:
            logger.error(
                f'Event {self.event_name} not fired. Exception: {exc}',
                extra={'payload': payload})
        else:
            logger.debug(f'Event {self.event_name} fired with message {message_id}')

        return message_id
