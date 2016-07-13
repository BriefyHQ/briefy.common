"""Briefy Event Queue."""
from briefy.common import validators
from briefy.common.config import EVENT_QUEUE
from briefy.common.queue import IQueue
from briefy.common.queue import Queue as BaseQueue
from briefy.common.utils.schema import Dictionary
from zope.interface import implementer

import colander


class Schema(colander.MappingSchema):
    """Payload for the event queue."""

    actor = colander.SchemaNode(colander.String(), validator=validators.empty_or(colander.uuid))
    created_at = colander.SchemaNode(colander.DateTime())
    data = colander.SchemaNode(Dictionary())
    event_name = colander.SchemaNode(colander.String(), validator=validators.EventName)
    guid = colander.SchemaNode(colander.String(), validator=colander.uuid)
    request_id = colander.SchemaNode(colander.String(),
                                     validator=validators.empty_or(colander.uuid))


@implementer(IQueue)
class Queue(BaseQueue):
    """A Queue to handle event messages between microservices."""

    name = EVENT_QUEUE
    _schema = Schema

    @property
    def payload(self):
        """Return an example payload for this queue.

        :returns: Dictionary representing the payload for this queue
        :rtype: dict
        """
        return {
            'event_name': '',
            'created_at': '',
            'guid': '',
            'actor': '',
            'request_id': '',
            'data': {}
        }

EventQueue = Queue()
