"""Briefy base events."""
from briefy.common.db import datetime_utcnow
from briefy.common.db.model import Base
from briefy.common.queue import IQueue
from briefy.common.queue.event import Queue
from briefy.common.users import SystemUser
from uuid import uuid4
from zope.component import getUtility
from zope.interface import Interface

import logging
import typing as t


logger = logging.getLogger(__name__)

Attributes = t.Optional[t.List[str]]


class IEvent(Interface):
    """Interface for Events on Briefy."""


class IDataEvent(IEvent):
    """Interface for data events on Briefy."""


class ITaskEvent(IEvent):
    """Interface for task events on Briefy."""


class Event:
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

    def __init__(self, guid: str, data: dict, actor: str, request_id: str):
        """Initialize the event.

        :param guid: ID of the object or data on this event
        :param data: Dictionary containing the payload to be used on the event message
        :param actor: The id of the user triggering this event.
        :param request_id: ID of the request triggering this event
        """
        self.data = data
        self.actor = actor if actor else ''
        self.id = str(uuid4())
        self.guid = guid
        self.request_id = request_id if request_id else ''
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
            'data': self.data,
        }
        message_id = ''
        try:
            message_id = queue.write_message(payload)
        except Exception as exc:
            logger.error(
                f'Event {self.event_name} not fired. Exception: {exc}',
                extra={'payload': payload}
            )
        else:
            logger.debug(f'Event {self.event_name} fired with message {message_id}')

        return message_id


class BaseEvent(Event):
    """A base event class used by all Briefy related events.

    Any event subclassing this one will write to an AWS SQS queue.
    """

    obj = None

    def __init__(self, obj: Base, actor: str='', request_id: str=''):
        """Initialize the event.

        :param obj: A SQLAlchemy object inheriting from briefy.common.db.models.Base
        :param actor: The id of the user triggering this event.
        :param request_id: ID of the request triggering this event
        """
        if not getattr(obj, 'created_at'):
            raise ValueError('Attempt to create event without a timestamp. Has it been persisted?')
        guid = getattr(obj, 'id')
        self.obj = obj
        data = self.to_dict()
        super().__init__(guid, data=data, actor=actor, request_id=request_id)

    def to_dict(self, excludes: Attributes=None, includes: Attributes=None) -> dict:
        """Return a serializable dictionary from the object that generated this event.

        :param excludes: attributes to exclude from dict representation.
        :param includes: attributes to include from dict representation.
        :returns: Dictionary with fields and values used by this Class
        """
        return self.obj.to_dict(excludes=excludes, includes=includes)


class TaskEvent(Event):
    """An event class to be specialized by Task Events."""

    def __init__(self, task_name: str, success: bool=True, data: dict=None, obj: Base=None):
        """Initialize the event.

        :param task_name: Name of the task triggering this event. i.e.: leica.pool_assign
        :param success: Was it successful or not?
        :param data: Dictionary containing the payload to be used on the event message
        :param obj: A SQLAlchemy object inheriting from briefy.common.db.models.Base
        """
        logger = self.logger
        if obj:
            guid = getattr(obj, 'id')
            if data:
                logger.warning('Both data and obj passed to event. Data is overridden')
            data = obj.to_dict()
        elif data:
            guid = data.get('id', '')
        else:
            msg = f'Task {self.event_name} event not fired. Exception: Need data or obj'
            logger.error(msg)
            raise ValueError(msg)
        actor = str(SystemUser.id)
        request_id = ''
        status = 'success' if success else 'failure'
        self.event_name = f'{task_name}.{status}'
        super().__init__(guid, data=data, actor=actor, request_id=request_id)
