"""Tests for `briefy.common.queue` package."""
from base_queue import BaseTest
from briefy.common.queue import Queue

import pytest


class TestQueue(BaseTest):
    """Tests for Base Queue."""

    queue = Queue

    def test_init(self):
        """Test queue name."""
        with pytest.raises(ValueError) as excinfo:
            self.queue()
        assert 'Queue must have a name' in str(excinfo.value)

    def test_repr(self):
        """Test str representation of this tool."""
        queue = self.queue
        with pytest.raises(ValueError) as excinfo:
            queue = queue()
            queue.__repr__()
        assert 'Queue must have a name' in str(excinfo.value)

    def test_write_message(self):
        """Test write_message."""
        queue = self.queue
        payload = self.get_payload()
        with pytest.raises(ValueError) as excinfo:
            queue = queue()
            queue.write_message(payload)
        assert 'Queue must have a name' in str(excinfo.value)

    def test_marshall_message(self):
        """Test _marshall_message."""
        queue = self.queue
        payload = self.get_payload()
        with pytest.raises(ValueError) as excinfo:
            queue = queue()
            queue._prepare_sqs_payload(payload)
        assert 'Queue must have a name' in str(excinfo.value)

    def test_get_messages(self):
        """Test get_messages."""
        queue = self.queue
        with pytest.raises(ValueError) as excinfo:
            queue = queue()
            queue.get_messages(num_messages=10)
        assert 'Queue must have a name' in str(excinfo.value)
