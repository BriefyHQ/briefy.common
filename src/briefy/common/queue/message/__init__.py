"""Briefy SQSMessage."""

from briefy.common.utils.schema import validate_and_serialize

import json
import colander


class SQSMessage:
    """A wrapped message to be used with a queue."""

    _message = None
    _schema = None
    _body = None

    def __init__(self, schema, message=None, body=None):
        """Initialize a Queue Message."""
        self._schema = schema
        if (message and body):
            raise ValueError('You should provide only one of message or body')
        elif (not message) and (not body):
            raise ValueError('You should provide a message or body')
        if message:
            self.message = message
        if body:
            self.body = body

    @property
    def schema(self):
        """Return the validation schema for this message."""
        return self._schema(unknown='ignore')

    @property
    def message(self):
        """Return the message."""
        message = self._message
        if not message:
            raise ValueError('No message available')
        return message

    @message.setter
    def message(self, value):
        """Process a message from amazon."""
        try:
            body = json.loads(value.body)
        except AttributeError:
            raise ValueError('Not a valid message')
        except json.decoder.JSONDecodeError:
            raise ValueError('Not a valid message body')
        schema = self.schema
        if schema:
            try:
                body = schema.deserialize(body)
            except colander.Invalid:
                raise ValueError('Not a valid message body')
        self._message = value
        self._body = body

    @property
    def body(self):
        """Return the body."""
        body = self._body
        if not body:
            raise ValueError('No body available')
        return body

    @body.setter
    def body(self, value):
        """Process a body for this message."""
        schema = self.schema
        if schema:
            try:
                value = validate_and_serialize(schema, value)
            except colander.Invalid as e:
                raise ValueError('Not a valid message body: {}'.format(str(e)))
        self._body = value

    def delete(self):
        """Delete this message from the Amazon SQS queue."""
        message = self.message
        message.delete()
        self._message = None
