"""Rests for briefy.common.queue.message."""
from briefy.common.config import SQS_REGION
from briefy.common.queue.message import SQSMessage

import boto3
import botocore.endpoint
import os
import pytest


@pytest.fixture
def queue_url():
    """Return the url for the SQS server."""
    host = os.environ.get('SQS_IP', '127.0.0.1')
    port = os.environ.get('SQS_PORT', '8080')
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
        messages = self.queue.receive_messages(MaxNumberOfMessages=1)
        return messages[0]
