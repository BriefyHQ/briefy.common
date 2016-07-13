"""Rests for briefy.common.queue.message."""
from briefy.common.queue.message import SQSMessage
from conftest import BaseSQSTest
from datetime import date
from datetime import datetime

import colander
import json
import pytest


class SimpleSchema(colander.MappingSchema):
    """Payload for this queue."""

    event_name = colander.SchemaNode(
        colander.String(),
        validator=colander.Regex(r'^(([a-z])+\.([a-z])+)+$')
    )


class TestSQSMessage(BaseSQSTest):

    schema = SimpleSchema

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


class DateSchema(colander.MappingSchema):
    """Payload for this queue."""

    date = colander.SchemaNode(
        colander.Date()
    )

    timestamp = colander.SchemaNode(
        colander.DateTime(default_tzinfo=None)
    )

    event_name = colander.SchemaNode(
        colander.String(),
        validator=colander.Regex(r'^(([a-z])+\.([a-z])+)+$')
    )


class TestSQSMessageWithDateTime(BaseSQSTest):
    """Test SQS Message."""

    queue = None
    schema = DateSchema

    def test_message_queue_preserves_time_data(self):
        """Test message roundtrip with date and datetime values."""
        today = date.today()
        now = datetime.now()
        body = {'event_name': 'job.created', 'date': today, 'timestamp': now}
        unbound_message = SQSMessage(self.schema, body=body)

        queue_message = self.create_message(json.dumps(unbound_message.body))

        message = SQSMessage(self.schema, message=queue_message)

        assert isinstance(message, SQSMessage)
        assert message.body['event_name'] == 'job.created'
        assert isinstance(message.body['date'], date)
        assert isinstance(message.body['timestamp'], datetime)
        assert message.body['date'] == today
        assert message.body['timestamp'] == now
