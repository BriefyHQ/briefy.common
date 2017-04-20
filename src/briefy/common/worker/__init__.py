"""Briefy base worker."""
# Make other workers available to common users
from .queue import QueueWorker  # noqa
from abc import ABCMeta
from abc import abstractmethod

import logging
import time


logger = logging.getLogger(__name__)


class Worker(metaclass=ABCMeta):
    """Base class for workers.

    Upon deriving from this, define a 'name' and the 'process' method.
    'run_interval' specifies the suspending time between two subsequent calls
    to self.process.

    The default timing function is time.sleep (thus making of this a
    single-threaded synchronous blocker worker) - you ay override
    that class or check for Worker mixins for threaded, multiprocessing
    or async versions.

    """

    name = ''
    run_interval = None

    def __init__(self, logger_=None, run_interval=None):
        """Initialize the worker.

        :param logger_: The logger instance to use or None
        :type logger_: A class that respects Python.logger interfaces
        :param run_interval: Minimum time ellapsed between sucessive calls to 'process'.
            Defaults to value specified on the class body
        :type run_interval: float or None
        :returns: None
        :rtype: NoneType
        """
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
        """Execute the worker.

        Calls "self.process" method in an infinite loop,
        sparsing the each call by self.run_interval seconds

        The code running in the process method, or code in another
        thread may set "self.running" to False to stop the worker
        """
        name = self.name
        self.logger.info('%s running', name)
        self.running = True
        while self.running:
            try:
                self.process()
            except Exception:
                self.logger.exception('{0}: Error executing process'.format(name))
            self.sleep(self.run_interval)
        self.logger.info('Exiting worker loop for {0}'.format(self.__class__))

    sleep = time.sleep


__all__ = ('Worker', 'QueueWorker')
