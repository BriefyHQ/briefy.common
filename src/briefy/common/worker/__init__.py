"""Briefy base worker."""
from time import sleep

import logging

logger = logging.getLogger(__name__)


class Worker:
    """Base class for workers."""

    name = ''
    sleep = None

    def __init__(self, logger_=None, sleep_=.5):
        """Initialize the worker."""
        self.logger = logger_ if logger_ else logger
        self.sleep = sleep_
        name = self.name
        if not name:
            raise ValueError('Worker must have a name')

    def process(self):
        """Run tasks on this worker."""
        raise NotImplementedError('Method not implemented')

    def __call__(self):
        """Execute the worker."""
        name = self.name
        self.logger.info('%s running', name)
        while True:
            try:
                self.process()
            except Exception:
                self.logger.exception('{}: Error executing process'.format(name))
            sleep(self.sleep)
