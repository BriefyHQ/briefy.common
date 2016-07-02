"""Base tests for briefy.common.queue."""
import boto3
import botocore.endpoint
import os


def get_url():
    """Return the url for the SQS server."""
    host = os.environ.get('SQS_IP', '127.0.0.1')
    port = os.environ.get('SQS_PORT', '8080')
    return 'http://{}:{}'.format(host, port)


class BaseTest:
    """Base tests for queues."""

    queue = None

    def _make_one(self):
        """Return a queue instance."""
        klass = self.queue
        sqs = boto3.resource('sqs', region_name=klass.region_name)
        sqs.create_queue(QueueName=klass.name)
        queue = sqs.get_queue_by_name(QueueName=klass.name)
        for message in queue.receive_messages(MaxNumberOfMessages=100):
            message.delete()
        return klass()

    def setup_class(cls):
        """Setup test class."""
        class MockEndpoint(botocore.endpoint.Endpoint):
            def __init__(self, host, *args, **kwargs):
                super().__init__(get_url(), *args, **kwargs)

        botocore.endpoint.Endpoint = MockEndpoint

    def get_payload(self):
        """Return a payload for this queue."""
        return {
            'foo': 'bar'
        }

    def test_init(self):
        """Test queue name."""
        queue = self._make_one()
        assert isinstance(queue, self.queue)

    def test_repr(self):
        """Test str representation of this tool."""
        queue = self._make_one()
        assert "<{0}(name='{1}'".format(queue.__class__.__name__, queue.name) in queue.__repr__()

    def test_write_message(self):
        """Test write_message."""
        queue = self._make_one()
        payload = self.get_payload()
        resp = queue.write_message(payload)
        assert isinstance(resp, str)

    def test_marshall_message(self):
        """Test _marshall_message."""
        queue = self._make_one()
        payload = self.get_payload()
        message = queue._message_klass(schema=queue.schema, body=payload)
        resp = queue._prepare_sqs_payload(message)
        assert isinstance(resp, dict)
        assert isinstance(resp['MessageBody'], str)

    def test_get_messages(self):
        """Test get_messages."""
        queue = self._make_one()
        payload = self.get_payload()
        resp = queue.write_message(payload)
        messages = queue.get_messages(num_messages=10)
        assert isinstance(messages, list)
        assert len(messages) == 1
        assert messages[0].message.message_id == resp
        assert messages[0].body == payload
