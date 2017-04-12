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

logger = logging.getLogger(__name__)


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


class BaseEvent(Event):
    """A base event class used by all Briefy related events.

    Any event subclassing this one will write to an AWS SQS queue.
    """

    def __init__(self, obj: Base, actor: str='', request_id: str=''):
        """Initialize the event.

        :param obj: A SQLAlchemy object inheriting from briefy.common.db.models.Base
        :param actor: The id of the user triggering this event.
        :param request_id: ID of the request triggering this event
        """
        if not getattr(obj, 'created_at'):
            raise ValueError('Attempt to create event without a timestamp. Has it been persisted?')
        guid = getattr(obj, 'id')
        data = obj.to_dict()
        super().__init__(guid, data=data, actor=actor, request_id=request_id)


class TaskEvent(Event):
    """An event class to be specialized by Task Events."""

    def __init__(self, task_name: str, success: bool=True, data: dict=None, obj: Base=None):
        """Initialize the event.

        :param task_name: Name of the task triggering this event. i.e.: leica.pool_assign
        :param success: Was it successful or not?
        :param data: Dictionary containing the payload to be used on the event message
        :param obj: A SQLAlchemy object inheriting from briefy.common.db.models.Base
        """
        if obj:
            guid = getattr(obj, 'id')
            data = obj.to_dict()
        elif data:
            guid = data.get('id', '')
        else:
            msg = 'Task {task_name} event not fired. Exception: {exc}'.format(
                task_name=self.event_name,
                exc='Need data or obj'
            )
            logger.error(msg)
            raise ValueError(msg)
        actor = str(SystemUser.id)
        request_id = ''
        self.event_name = '{task_name}.{status}'.format(
            task_name=task_name,
            status='success' if success else 'failure'
        )
        super().__init__(guid, data=data, actor=actor, request_id=request_id)
