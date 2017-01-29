"""Briefy base events."""
from briefy.common.db import datetime_utcnow
from briefy.common.queue import IQueue
from briefy.common.queue.event import Queue
from uuid import uuid4
from zope.component import getUtility
from zope.interface import Interface

import logging

logger = logging.getLogger(__name__)


class IEvent(Interface):
    """Interface for Events on Briefy."""


class IDataEvent(IEvent):
    """Interface for data events on Briefy."""


class BaseEvent:
    """A base event class used by all Briefy related events.

    Any event subclassing this one will write to an AWS SQS queue.
    """

    event_name = ''
    """Name of the event."""

    actor = ''
    """ID of the actor triggering this event."""

    id = ''
    """ID of this event."""

    guid = ''
    """ID of the object."""

    created_at = ''
    """Datetime of the event."""

    request_id = ''
    """ID of the request.

    This is useful for web transactions.
    """

    logger = logger
    data = None
    obj = None

    def __init__(self, obj, actor=None, request_id=None):
        """Initialize the event."""
        if not obj.created_at:
            raise ValueError('Attempt to create event without a timestamp. Has it been persisted?')
        guid = obj.id
        self.obj = obj
        self.actor = actor
        self.id = str(uuid4())
        self.guid = guid
        self.request_id = request_id
        self.created_at = datetime_utcnow()

    @property
    def queue(self) -> Queue:
        """Return the events queue."""
        return getUtility(IQueue, 'events.queue')

    def __call__(self) -> str:
        """Notify about the event.

        :returns: Id from message in the queue
        """
        logger = self.logger
        queue = self.queue
        payload = {
            'event_name': self.event_name,
            'actor': self.actor,
            'id': self.id,
            'guid': self.guid,
            'created_at': self.created_at,
            'request_id': self.request_id,
            'data': self.obj.to_dict(),
        }
        message_id = ''
        try:
            message_id = queue.write_message(payload)
        except Exception as e:
            logger.error(
                'Event {name} not fired. Exception: {exc}'.format(
                    name=self.event_name,
                    exc=e
                ),
                extra={'payload': payload})
        else:
            logger.debug(
                'Event {name} fired with message {id_}'.format(
                    name=self.event_name,
                    id_=message_id
                )
            )

        return message_id
