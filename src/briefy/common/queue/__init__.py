"""Briefy Queue."""
from botocore.exceptions import ClientError
from briefy.common.config import SQS_REGION
from briefy.common.utils.transformers import json_dumps
from briefy.common.queue.message import SQSMessage
from datetime import datetime
from zope.interface import Attribute
from zope.interface import Interface

import boto3
import json
import logging

logger = logging.getLogger(__name__)


class IQueue(Interface):
    """Interface for a Queue."""

    name = Attribute("""Queue name.""")
    region_name = Attribute("""SQS Region name.""")
    origin = Attribute("""Package name.""")


class Queue:
    """A Queue that manage messages from a SQS Queue."""

    name = ''
    region_name = SQS_REGION
    origin = ''
    _queue = None
    _schema = None
    _message_klass = SQSMessage

    def __init__(self, origin='briefy.common', logger_=None):
        """Initialize a Queue object."""
        self.logger = logger_ if logger_ else logger
        self.origin = origin
        name = self.name
        if not name:
            raise ValueError('Queue must have a name')

    @property
    def payload(self):
        """Return an example payload for this queue.

        :returns: Dictionary representing the payload for this queue
        :rtype: dict
        """
        return {}

    @property
    def queue(self):
        """Return a SQS queue."""
        queue = self._queue
        if not queue:
            name = self.name
            region_name = self.region_name
            try:
                sqs = boto3.resource('sqs', region_name=region_name)
                queue = sqs.get_queue_by_name(QueueName=name)
            except ClientError:
                error_message = 'Error getting queue named {} in the {} region'.format(
                    name, region_name
                )
                self.logger.exception(error_message)
                raise ValueError(error_message)
            self._queue = queue
        return queue

    @property
    def schema(self):
        """Payload schema for this queue.

        :returns: A Schema to be used to validate messages in this queue
        :rtype: colander.MappingSchema
        """
        schema = self._schema
        return schema

    def _create_sqs_message(self, message=None, body=None):
        """Create a new SQSMessage."""
        klass = self._message_klass
        return klass(self.schema, message, body)

    def get_raw_messages(self, num_messages=1):
        """Return messages from the queue.

        :param num_messages: Number of messages to be returned
        :type num_messages: int
        :returns: List of messages
        :rtype: list
        """
        queue = self.queue
        messages = queue.receive_messages(MaxNumberOfMessages=num_messages)
        return messages

    def get_messages(self, num_messages=1):
        """Return validated messages from the queue.

        :param num_messages: Number of messages to be returned
        :type num_messages: int
        :returns: List of SQSMessages
        :rtype: list
        """
        messages = []
        raw_messages = self.get_raw_messages(num_messages)
        for message in raw_messages:
            try:
                new_message = self._create_sqs_message(message=message)
            except ValueError as e:
                logger.exception('{}'.format(str(e)))
            else:
                messages.append(new_message)
        return messages

    def write_messages(self, messages=()):
        """Write messages to the queue.

        :param messages: List of messages to be added to queue
        :type messages: list
        """
        if not isinstance(messages, list):
            raise ValueError
        for message in messages:
            self.write_message(message)

    def _prepare_sqs_payload(self, message):
        """Prepare a SQS send payload.

        :param message: A message wrapper representing the message to be added to the queue
        :type message: `briefy.common.queue.message.Message`
        :returns: A dict with all parameters to the send_message method.
        :rtype: dict
        """
        payload = {
            'MessageBody': json_dumps(message.body),
            'MessageAttributes': {
                'Origin': {'StringValue': self.origin, 'DataType': 'String'},
                'Author': {'StringValue': self.__class__.__name__, 'DataType': 'String'},
                'CreationDate': {'StringValue': str(datetime.now()), 'DataType': 'String'}
            }
        }
        return payload

    def write_message(self, body=None):
        """Write a message to the queue.

        :param body: A dictionary representing the message to be added to the queue
        :type body: dict
        """
        queue = self.queue
        try:
            message = self._create_sqs_message(body=body)
        except ValueError as e:
            logger.exception('{}'.format(str(e)))
            raise e
        payload = self._prepare_sqs_payload(message)
        response = queue.send_message(**payload)
        message_id = response.get('MessageId')
        return message_id.strip() if message_id else ''

    def __repr__(self):
        """Representation of a Queue."""
        return (
            """<{0}(name='{1}' region='{2}')>""").format(
                self.__class__.__name__,
                self.name,
                self.region_name
        )
