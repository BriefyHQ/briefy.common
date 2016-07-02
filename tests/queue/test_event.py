"""Tests for `briefy.common.queue.event` module."""
from base_queue import BaseTest
from briefy.common.queue.event import Queue
from datetime import datetime

import pytz


class TestEventQueue(BaseTest):
    """Tests for EventQueue."""

    queue = Queue
    utility_name = 'events.queue'

    def get_payload(self):
        """Payload for the event queue."""
        return {
            'event_name': 'customer.event.created',
            'created_at': datetime(2016, 6, 21, 18, 34, 22, tzinfo=pytz.utc),
            'guid': 'eebd5265-7201-4316-b996-722b977dbf32',
            'actor': '8cfe3809-30e5-4589-a8b2-32afd75483dd',
            'request_id': 'e8980ee1-37c3-43fc-8da0-973017f198ab',
            'data': {
                'foo': 'bar',
                'bar': 'foo'
            }
        }

    def test_interfaces(self):
        """Test that this queue provides IQueue interfaces."""
        from briefy.common.queue import IQueue
        queue = self.queue()
        assert IQueue.providedBy(queue)

    def test_utility_lookup(self):
        """Test that this queue provides IQueue interfaces."""
        from briefy import common
        from briefy.common.queue import IQueue
        from zope.component import getUtility
        from zope.configuration.xmlconfig import XMLConfig

        XMLConfig('configure.zcml', common)()
        queue = getUtility(IQueue, self.utility_name)
        assert isinstance(queue, self.queue)
