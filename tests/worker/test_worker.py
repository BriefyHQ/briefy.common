"""Tests for `briefy.common.worker.Worker`."""
from briefy.common.worker import Worker
from conftest import MockLogger

import pytest
import time


class MinimalWorker(Worker):
    """Minimal worker."""

    name = 'Minimal'
    run_interval = 0.01
    _count = 0
    _runs = 5

    def process(self):
        """Run tasks on this worker."""
        self._count += 1
        if self._count >= self._runs:
            self.running = False


def test_worker_is_not_isntantiated_without_a_process_method():
    """Assert worker class needs an overrided process method."""
    with pytest.raises(TypeError):
        Worker()

    class NonProcessWorker(Worker):
        name = 'Faulty'

    with pytest.raises(TypeError):
        NonProcessWorker()


def test_worker_is_not_isntantiated_without_a_name():
    """Assert worker class needs a set name."""
    class NonNamedWorker(Worker):
        def process(self):
            pass

    with pytest.raises(ValueError):
        NonNamedWorker()


def test_worker_calls_process_functions():
    """Assert worker calls process."""
    w = MinimalWorker()
    w()
    assert w._count == w._runs


def test_worker_respect_run_interval():
    """Assert worker respects run_interval."""
    tolerance = 0.2
    for w in (MinimalWorker(), MinimalWorker(run_interval=0.03)):
        start = time.time()
        w()
        end = time.time()
        expected_time = w.run_interval * w._runs
        min_time = expected_time - expected_time * tolerance
        max_time = expected_time + expected_time * tolerance
        assert min_time < end - start < max_time


def test_worker_calls_logger():
    """Assert worker calls logger."""
    class RaiserWorker(Worker):
        name = 'raiser'
        run_interval = 0.01

        def process(self):
            self.running = False
            raise RuntimeError

    mock_logger = MockLogger()
    w = RaiserWorker(logger_=mock_logger)
    w()
    assert mock_logger.info_called and mock_logger.exception_called
