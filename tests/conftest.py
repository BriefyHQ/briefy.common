"""Rests for briefy.common.queue.message."""
import briefy.common  # noQA make sure sqlalchemy_continuum is initialized first
from briefy.common.config import SQS_REGION
from briefy.common.db import Base
from briefy.common.db.models import Item
from briefy.common.db.models.local_role import LocalRole
from briefy.common.db.models.roles import LocalRoleDeprecated
from briefy.common.queue import IQueue
from prettyconf import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch
from unittest.mock import PropertyMock
from zope import component
from zope.configuration.xmlconfig import XMLConfig

import boto3
import botocore.endpoint
import json
import os
import pytest
import requests


XMLConfig('configure.zcml', briefy.common)()
DBSession = scoped_session(sessionmaker())


@pytest.fixture(scope='class')
def sql_engine(request):
    """Create new engine based on db_settings fixture.
    :param request: pytest request
    :return: sqlalcheny engine instance.
    """
    database_url = config('DATABASE_URL',
                          default='postgresql://briefy:briefy@127.0.0.1:9999/briefy-common')
    engine = create_engine(database_url, echo=False)
    DBSession.configure(bind=engine)
    LocalRoleDeprecated.__session__ = DBSession
    Item.__session__ = DBSession
    LocalRole.__session__ = DBSession
    Base.metadata.create_all(engine)

    def teardown():
        Base.metadata.drop_all(engine)

    request.addfinalizer(teardown)
    return engine


@pytest.fixture(scope='class')
def db_transaction(request, sql_engine):
    """Create a transaction for each test class.
    :param request: pytest request
    :param sql_engine: sqlalchemy engine (fixture)
    :return: sqlalchemy connection
    """
    connection = sql_engine.connect()
    transaction = connection.begin()
    DBSession.configure(bind=connection)

    def teardown():
        transaction.rollback()
        connection.close()
        DBSession.remove()

    request.addfinalizer(teardown)
    return connection


@pytest.fixture(scope='class')
def session(request):
    """Return session from database.
    :returns: A SQLAlchemy scoped session
    :rtype: sqlalchemy.orm.scoped_session
    """
    db_session = DBSession()

    def teardown():
        DBSession.remove()

    request.addfinalizer(teardown)
    return db_session


# Python's unittest.mock assertions requires the exact parameters to the method
# to match the assertion. That wpud bind the error messages to the test
class MockLogger:
    info_called = 0
    exception_called = 0

    def __init__(self):
        self.info_messages = []
        self.exception_messages = []

    def info(self, *args, **kw):
        self.info_messages.append(args[0])
        self.info_called += 1

    def exception(self, *args, **kw):
        self.exception_messages.append(args[0])
        self.exception_called += 1

    def debug(self, *args, **kw):
        pass

    def error(self, *args, **kw):
        pass

    def __call__(self, *args, **kw):
        pass


@pytest.fixture
def queue_url():
    """Return the url for the SQS server."""
    host = os.environ.get('SQS_IP', '127.0.0.1')
    port = os.environ.get('SQS_PORT', '5000')
    return 'http://{0}:{1}'.format(host, port)


@pytest.fixture
def cache_manager(request, backend, enable_refresh):
    """Return the registered ICacheManager utility."""
    _backend = PropertyMock(return_value=backend)
    _enable_refresh = PropertyMock(return_value=enable_refresh)
    backend_patch = patch(
        'briefy.common.cache.BaseCacheManager._backend',
        _backend
    )
    backend_patch.start()

    refresh_patch = patch(
        'briefy.common.cache.BaseCacheManager._enable_refresh',
        _enable_refresh
    )
    refresh_patch.start()

    def finalizer():
        backend_patch.stop()
        refresh_patch.stop()

    request.addfinalizer(finalizer)

    from briefy.common.cache import ICacheManager
    from zope.component import getUtility
    return getUtility(ICacheManager)


class BaseSQSTest:
    """Test SQS Message."""

    queue = None
    schema = None

    def _setup_queue(self):
        """Return a queue instance."""
        name = 'foobar'
        sqs = boto3.resource('sqs', region_name=SQS_REGION)
        sqs.create_queue(QueueName=name)
        self.queue = sqs.get_queue_by_name(QueueName=name)

        for message in self.queue.receive_messages(MaxNumberOfMessages=100):
            message.delete()

    def setup_class(cls):
        """Setup test class."""
        class MockEndpoint(botocore.endpoint.Endpoint):
            def __init__(self, host, *args, **kwargs):
                super().__init__(queue_url(), *args, **kwargs)

        botocore.endpoint.Endpoint = MockEndpoint

    def create_message(self, body):
        """Create a message in the queue, retrieve it from there, and return it."""
        self._setup_queue()
        payload = {'MessageBody': body}

        self.queue.send_message(**payload)
        return self.get_from_queue()

    def get_from_queue(self):
        messages = self.queue.receive_messages(MaxNumberOfMessages=1)
        return messages[0]


class BriefyQueueBaseTest(BaseSQSTest):

    def _setup_queue(self):
        super()._setup_queue()
        from briefy.common.queue.event import EventQueue
        EventQueue._queue = self.queue
        component.provideUtility(EventQueue, IQueue, 'events.queue')


def _mock_thumbor(self, method, url, *args, **kwargs):
    """Mock request to briefy-thumbor."""
    status_code = 200
    filename = 'utils/thumbor.json'
    headers = {
        'content-type': 'application/json',
    }
    data = open(os.path.join(__file__.rsplit('/', 1)[0], filename)).read()
    resp = requests.Response()
    resp.status_code = status_code
    resp.headers = headers
    resp._content = data.encode('utf8')
    return resp


def _mock_test_endpoint(self, method, url, *args, **kwargs):
    """Mock test endpoint."""
    data = None
    status_code = 200

    if method == 'get':
        params = kwargs.get('params')
        result = {'title': 'The Title', 'description': 'The Description'}
        # this is a query in collection_get
        if params and params.get('_items_per_page'):
            data = {
                'data': [result],
                'pagination': {
                    'total': 1,
                    'page': 1,
                    'page_count': 1,
                    'items_per_page': params.get('_items_per_page'),
                    'previous_page': None,
                    'next_page': None,
                }
            }
        else:
            data = result
    elif method in ('post', 'put'):
        data = kwargs['data']
        data = json.loads(data)
    else:
        status_code = 404

    headers = {
        'content-type': 'application/json',
    }
    resp = requests.Response()
    resp.status_code = status_code
    resp.headers = headers
    resp._content = json.dumps(data).encode('utf8')
    return resp


def _mock_rolleiflex(self, method, url, *args, **kwargs):
    status_code = 200
    filename = 'data/rolleiflex_login.json'
    headers = {
        'content-type': 'application/json',
    }
    data = open(os.path.join(__file__.rsplit('/', 1)[0], filename)).read()
    resp = requests.Response()
    resp.status_code = status_code
    resp.headers = headers
    resp._content = data.encode('utf8')
    return resp


@pytest.fixture(scope='session')
def mock_requests():
    """Mock external requests."""
    def mock_requests_response(self, method, url, *args, **kwargs):
        """Mock a response"""
        if 'briefy-rolleiflex' in url or 'login/email' in url:
            return _mock_rolleiflex(self, method, url, *args, **kwargs)
        elif 'test-service' in url:
            return _mock_test_endpoint(self, method, url, *args, **kwargs)
        elif 'briefy-thumbor' in url:
            return _mock_thumbor(self, method, url, *args, **kwargs)

    return mock_requests_response


@pytest.fixture(autouse=True)
def mock_api(monkeypatch, mock_requests):
    """Mock all api calls."""
    monkeypatch.setattr(requests.sessions.Session, 'request', mock_requests)
