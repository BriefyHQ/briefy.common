"""Rests for briefy.common.queue.message."""
from base_queue import get_url
from briefy.common.config import SQS_REGION
from briefy.common.queue.message import SQSMessage

import boto3
import colander
import botocore.endpoint
import json
import pytest


class SimpleSchema(colander.MappingSchema):
    """Payload for this queue."""

    event_name = colander.SchemaNode(
        colander.String(),
        validator=colander.Regex(r'^(([a-z])+\.([a-z])+)+$')
    )


class TestSQSMessage:
    """Test SQS Message."""

    queue = None
    schema = SimpleSchema

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
                super().__init__(get_url(), *args, **kwargs)

        botocore.endpoint.Endpoint = MockEndpoint

    def create_message(self, body):
        """Create a message in the queue and return it."""
        self._setup_queue()
        payload = {'MessageBody': body}
        self.queue.send_message(**payload)
        messages = self.queue.receive_messages(MaxNumberOfMessages=1)
        return messages[0]

    def test_init_with_valid_body(self):
        """Test message with a valid body."""
        body = {'event_name': 'job.created'}
        message = SQSMessage(self.schema, body=body)

        assert isinstance(message, SQSMessage)
        assert message.body == body

    def test_init_with_additional_fields(self):
        """Test message with a valid body."""
        body = {'event_name': 'job.created', 'foo': 'bar'}
        message = SQSMessage(self.schema, body=body)

        assert isinstance(message, SQSMessage)
        assert message.body == {'event_name': 'job.created'}

    def test_init_with_invalid_body(self):
        """Test message with a valid body."""
        body = {'foo': 2}
        with pytest.raises(ValueError) as excinfo:
            SQSMessage(self.schema, body=body)

        assert "{'event_name': 'Required'}" in str(excinfo.value)

        body = {'event_name': 2}
        with pytest.raises(ValueError) as excinfo:
            SQSMessage(self.schema, body=body)

        assert 'String does not match expected pattern' in str(excinfo.value)

        body = {'event_name': 'job.'}
        with pytest.raises(ValueError) as excinfo:
            SQSMessage(self.schema, body=body)

        assert 'String does not match expected pattern' in str(excinfo.value)

    def test_init_with_valid_queue_message(self):
        """Test message with a valid sqs message."""
        body = json.dumps({'event_name': 'job.created', 'foo': 'bar'})
        queue_message = self.create_message(body)

        message = SQSMessage(self.schema, message=queue_message)

        assert isinstance(message, SQSMessage)
        assert message.body == {'event_name': 'job.created'}

    def test_init_with_invalid_queue_message(self):
        """Test message with an invalid sqs message."""
        body = json.dumps('event_name')
        queue_message = self.create_message(body)

        with pytest.raises(ValueError) as excinfo:
            SQSMessage(self.schema, message=queue_message)

        assert 'Not a valid message body' in str(excinfo.value)

    def test_delete_message(self):
        """Test deleting a message from the sqs queue."""
        body = json.dumps({'event_name': 'job.created'})
        queue_message = self.create_message(body)

        message = SQSMessage(self.schema, message=queue_message)
        message.delete()

        with pytest.raises(ValueError) as excinfo:
            message.message

        assert 'No message available' in str(excinfo.value)
