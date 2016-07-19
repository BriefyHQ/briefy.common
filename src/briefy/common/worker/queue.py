"""Briefy base worker."""
from briefy.common.worker import Worker


class QueueWorker(Worker):
    """Base class for workers."""

    name = ''
    input_queue = None
    run_interval = None

    def __init__(self, logger_=None, run_interval=.5):
        """Initialize the worker."""
        super().__init__(logger_, sleep_)
        queue = self.input_queue
        if not queue:
            raise ValueError('Queue Worker must have a queue')

    def get_messages(self):
        """Get messages from self.input_queue.

        :returns: A list of boto3.resources.factory.sqs.Message objects
        :rtype: list
        """
        messages = self.input_queue.get_messages()
        self.logger.debug('Got {} messages'.format(len(messages)))
        return messages

    def process_message(self, message):
        """Process a message retrieved from the input_queue.

        :param message: A message from the queue
        :type message: boto3.resources.factory.sqs.Message
        :returns: Status from the process
        :rtype: bool
        """
        status = True
        return status

    def process(self):
        """Run tasks on this worker."""
        messages = self.get_messages()
        for message in messages:
            if self.process_message(message):
                message.delete()
            else:
                # TODO: Improve error handling here
                self.logger.info('Message was not deleted')
