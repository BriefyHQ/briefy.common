"""Briefy Event Queue."""
from briefy.common.config import EVENT_QUEUE
from briefy.common.queue import IQueue
from briefy.common.queue import Queue as BaseQueue
from zope.interface import implementer


@implementer(IQueue)
class Queue(BaseQueue):
    """A Queue to handle event messages between microservices."""

    name = EVENT_QUEUE

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
