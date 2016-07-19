"""Briefy base worker."""
from abc import ABCMeta
from abc import abstractmethod

import logging
import time

logger = logging.getLogger(__name__)


class Worker(metaclass=ABCMeta):
    """Base class for workers."""

    name = ''
    run_interval = None

    def __init__(self, logger_=None, run_interval=None):
        """Initialize the worker."""
        self.logger = logger_ if logger_ else logger
        if run_interval is not None:
            self.run_interval = run_interval
        name = self.name
        if not name:
            raise ValueError('Worker must have a name')

    @abstractmethod
    def process(self):  # pragma: no cover
        """Run tasks on this worker."""
        raise NotImplementedError('Method not implemented')

    def __call__(self):
        """Execute the worker."""
        name = self.name
        self.logger.info('%s running', name)
        self.running = True
        while self.running:
            try:
                self.process()
            except Exception:
                self.logger.exception('{}: Error executing process'.format(name))
            self.sleep(self.run_interval)
        self.logger.info('Exiting worker loop for {}'.format(self.__class__))

    sleep = time.sleep




# Make other workers available to common users
from .queue import QueueWorker # noqa

__all__ = [Worker, QueueWorker]
