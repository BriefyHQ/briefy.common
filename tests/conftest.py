"""Rests for briefy.common.queue.message."""
from briefy.common.config import SQS_REGION
from briefy.common.queue import IQueue
from zope import component

import boto3
import botocore.endpoint
import os
import pytest


# Python's unittest.mock assertions requires the exact parameters to the method
# to match the assertion. That wpud bind the error messages to the test
class MockLogger:
    info_called = 0
    exception_called = 0

    def __init__(self):
        self.info_messages = []
        self.exception_messages = []

    def info(self, *args, **kw):
        self.info_messages.append(args[0])
        self.info_called += 1

    def exception(self, *args, **kw):
        self.exception_messages.append(args[0])
        self.exception_called += 1

    def debug(self, *args, **kw):
        pass

    def error(self, *args, **kw):
        pass

    def __call__(self, *args, **kw):
        pass


@pytest.fixture
def queue_url():
    """Return the url for the SQS server."""
    host = os.environ.get('SQS_IP', '127.0.0.1')
    port = os.environ.get('SQS_PORT', '5000')
    return 'http://{}:{}'.format(host, port)


class BaseSQSTest:
    """Test SQS Message."""

    queue = None
    schema = None

    def _setup_queue(self):
        """Return a queue instance."""
        name = 'foobar'
        sqs = boto3.resource('sqs', region_name=SQS_REGION)
        sqs.create_queue(QueueName=name)
        self.queue = sqs.get_queue_by_name(QueueName=name)

        for message in self.queue.receive_messages(MaxNumberOfMessages=100):
            message.delete()

    def setup_class(cls):
        """Setup test class."""
        class MockEndpoint(botocore.endpoint.Endpoint):
            def __init__(self, host, *args, **kwargs):
                super().__init__(queue_url(), *args, **kwargs)

        botocore.endpoint.Endpoint = MockEndpoint

    def create_message(self, body):
        """Create a message in the queue, retrieve it from there, and return it."""
        self._setup_queue()
        payload = {'MessageBody': body}

        self.queue.send_message(**payload)
        return self.get_from_queue()

    def get_from_queue(self):
        messages = self.queue.receive_messages(MaxNumberOfMessages=1)
        return messages[0]


class BriefyQueueBaseTest(BaseSQSTest):

    def _setup_queue(self):
        super()._setup_queue()
        from briefy.common.queue.event import EventQueue
        EventQueue._queue = self.queue
        component.provideUtility(EventQueue, IQueue, 'events.queue')
