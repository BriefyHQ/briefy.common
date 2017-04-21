"""Tests for `briefy.common.worker.queue.QueueWorker`."""
from briefy.common.worker import QueueWorker
from conftest import MockLogger

import pytest
import time


# FIXME: a call to SQS get_messages is NOT deterministic
# the docker-based SQS implementaiton makes it so that most times
# new messages on the queue are read on the subsequent call.
# But it also emulates the non-deterministic behavior, in that
# older repeated calls to queue.get_messages may fail to
# actually retrieve any messages.

# the tests here,as they are now,  do not take the non-deterministic
# behavior into account and do fail if using the emulator

# Reference: http://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ReceiveMessage.html  # noqa

# TODO: create integration tests and improve the code to
# actually test using the emulator.
# We are using a DummyQueue for now, that asserts
# coverage and behavior of code when messages are returned.


class MinimalMessage:
    """Minimal message."""

    def __init__(self, owner, body):
        """Initialize the object."""
        self.body = body
        self.owner = owner

    def delete(self):
        """Delete message from owner."""
        for i, message in enumerate(self.owner.messages):
            if message == self.body:
                del self.owner.messages[i]
                break


class DummyQueue:
    """Dummy queue."""

    def __init__(self):
        """Initialize dummy queue."""
        self.messages = []

    def write_message(self, payload):
        """Write message to the queue."""
        self.messages.append(payload)

    def get_messages(self):
        """Return a list of MinimalMessage from this queue."""
        return [MinimalMessage(self, message) for message in self.messages]


class MinimalQueueWorker(QueueWorker):
    """A Queue worker."""

    name = 'Minimal'
    region_name = 'mock_region.east.1'
    _counter = 0
    _iterations = 1
    run_interval = 0.01

    def __init__(self, *args, **kw):
        """Initialize the worker."""
        self._counter = 0
        super().__init__(*args, **kw)

    def process(self):
        """Run tasks on this worker."""
        self._counter += 1
        if self._counter >= self._iterations:
            self.running = False
        return super().process()


class TestQueueWorker:
    """Testcase for queue worker."""

    queue = DummyQueue

    def get_payload(self):
        """Return a payload for this queue."""
        return {'message': 'bar'}

    def test_queue_worker_needs_a_queue(self):
        """Queue worker always needs a queue."""
        with pytest.raises(ValueError):
            MinimalQueueWorker(None)

    def test_queue_worker_consume_messages(self):
        """Test write_message."""
        queue = self.queue()
        w = MinimalQueueWorker(queue)
        payload = self.get_payload()
        queue.write_message(payload)
        test_results = list(queue.get_messages())
        assert len(test_results) == 1
        test_results[0].delete()
        queue.write_message(payload)
        w()
        assert len(list(queue.get_messages())) == 0

    def test_threaded_queue_worker_consume_messages(self):
        """Test write_message."""
        from threading import Thread  # noQA
        queue = self.queue()
        w = MinimalQueueWorker(queue)
        w._iterations = 100
        payload = self.get_payload()

        t = Thread(target=w)

        queue.write_message(payload)
        t.start()
        time.sleep(0.6)
        assert len(list(queue.get_messages())) == 0
        w.running = False
        t.join()

    def test_queue_worker_logs_non_processed_messages(self):
        """Test write_message."""
        queue = self.queue()

        class FailingQueueWorker(MinimalQueueWorker):
            def process_message(self, message):
                return False

        mock_logger = MockLogger()
        w = FailingQueueWorker(queue, logger_=mock_logger)
        payload = self.get_payload()
        queue.write_message(payload)
        w()
        assert len(list(queue.get_messages())) == 1
        assert 'Message was not deleted' in mock_logger.info_messages
