"""Briefy workflow events."""
from briefy.common.event import BaseEvent
from briefy.common.event import IDataEvent
from briefy.common.event import logger
from zope.interface import implementer


class IWorkflowTransitionEvent(IDataEvent):
    """IDataEvent interface for a workflow transition in a workflow."""


@implementer(IWorkflowTransitionEvent)
class WorkflowTranstionEvent(BaseEvent):
    """Base class for workflow transition events that will be queued on sqs."""

    logger = logger

    @property
    def event_name(self):
        """Automatic generate event name from model class name and transation name."""
        model_name = self.obj.__class__.__name__.lower()
        transition_name = self.transition.name
        name = '{model_name}.workflow.{transition_name}'
        return name.format(model_name=model_name, transition_name=transition_name)

    def __init__(self, obj, request, transition, user=None):
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
        kwargs = dict(actor=user_id, request_id=None)
        super().__init__(obj, **kwargs)

    def __call__(self):
        """Notify about the event.

        :returns: Id from message in the queue
        :rtype: str
        """
        logger = self.logger
        queue = self.queue
        payload = {
            'event_name': self.event_name,
            'actor': self.actor,
            'guid': self.guid,
            'created_at': self.created_at,
            'request_id': self.request_id,
            'data': self.obj.to_dict(),
            'transition': self.transition.name,
        }
        message_id = ''
        try:
            message_id = queue.write_message(payload)
        except Exception as e:
            logger.error('Event {} not fired. Exception: {}'.format(self.event_name, e),
                         extra={'payload': payload})
        else:
            logger.debug('Event {} fired with message {}'.format(self.event_name, message_id))

        return message_id
