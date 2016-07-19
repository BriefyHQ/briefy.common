from briefy.common.worker import Worker

import pytest

class MinimalWorker(Worker):
    name = 'Minimal'
    sleep = 0.1

    def process(self):
        pass


def test_worker_is_not_isntantiated_without_a_process_method():
    """Asserts worker class needs an overrided process method

    """
    with pytest.raises(TypeError):
        w = Worker()

    class NonProcessWorker(Worker):
        name = 'Faulty'

    with pytest.raises(TypeError):
        w = NonProcessWorker()

def test_worker_is_not_isntantiated_without_a_name():
    """Asserts worker class needs a set name and"""

    class NonNamedWorker(Worker):
        def process(self):
            pass

    with pytest.raises(ValueError):
        w = NonNamedWorker()

#def test_worker_does_not_hang_if_called_without_a_proper_process():
    #"""Asserts worker class needs a set name and override process

    #"""
    #with pytest.raises(ValueError):
        #w = Worker()

    #class NonCallableWorker(Worker):
        #name = 'Faulty'

    #with pytest.raises(NotImplementedError):
        #w = NonCallableWorker()
        #assert w
        #w()
