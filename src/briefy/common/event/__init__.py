"""Briefy base events."""
from briefy.common.queue import IQueue
from zope.component import getUtility
from zope.interface import Interface

import json
import logging

logger = logging.getLogger(__name__)


class IEvent(Interface):
    """Interface for Events on Briefy."""


class IDataEvent(IEvent):
    """Interface for data events on Briefy."""


class BaseEvent:
    """A base event class for briefy."""

    event_name = ''
    actor = ''
    guid = ''
    created_at = ''
    request_id = ''
    logger = logger
    data = None

    def __init__(self, obj, actor=None, request_id=None):
        """Initialize the event."""
        if not obj.created_at:
            raise ValueError('Attempt to create event without a timestamp. Has it been persisted?')
        guid = obj.id
        self.actor = actor
        self.guid = guid
        self.request_id = request_id
        self.created_at = obj.created_at
        self.data = obj.to_JSON()

    @property
    def queue(self):
        """Return the events queue."""
        return getUtility(IQueue, 'events.queue')

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
            'data': json.loads(self.data),
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
