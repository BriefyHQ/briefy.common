"""Briefy Queue."""
from botocore.exceptions import ClientError
from briefy.common.config import SQS_REGION
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

    def get_messages(self, num_messages=1):
        """Return messages from the queue.

        :param num_messages: Number of messages to be returned
        :type num_messages: int
        :returns: List of messages
        :rtype: list
        """
        queue = self.queue
        messages = queue.receive_messages(MaxNumberOfMessages=num_messages)
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

        :param message: A dictionary representing the message to be added to the queue
        :type message: dict
        :returns: A dict with all parameters to the send_message method.
        :rtype: dict
        """
        payload = {
            'MessageBody': json.dumps(message),
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
        payload = self._prepare_sqs_payload(body)
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
