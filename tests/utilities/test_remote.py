"""Test IRemoteRestEndpoint utility"""
from briefy.common.utilities.interfaces import IRemoteRestEndpoint
from zope.component import getUtility
from zope.interface import implementedBy

import pytest
import uuid


POST_DATA = [
    {'title': 'The Title', 'description': 'The Description'}
]
PUT_DATA = [
    ({'title': 'New Title', 'description': 'New Description'}, uuid.uuid4(), )
]
ITEM_UUID = [
    uuid.uuid4()
]


@pytest.fixture(scope='module')
def get_remote_rest_utility():
    """Fixture to create a new remote rest utility instance."""
    uri = 'http://test-service'
    path = '/endpoint'
    name = 'Test Endpoint'
    factory = getUtility(IRemoteRestEndpoint)
    return factory(uri, path, name)


class TestRemoteRestEndoint:
    """Test remote rest endpoint utility."""

    def test_get_utility(self, get_remote_rest_utility):
        """Query utility and execute operations."""
        remote = get_remote_rest_utility
        assert implementedBy((remote, IRemoteRestEndpoint))

    @pytest.mark.parametrize('data', POST_DATA)
    def test_post_item(self, get_remote_rest_utility, data):
        """Test add a new item in the remote rest endpoint."""
        remote = get_remote_rest_utility
        result = remote.post(data)
        assert isinstance(result, dict)

    @pytest.mark.parametrize('uid', ITEM_UUID)
    def test_get_item(self, get_remote_rest_utility, uid):
        """Test add a new item in the remote rest endpoint."""
        remote = get_remote_rest_utility
        result = remote.get(uid)
        assert isinstance(result, dict)

    @pytest.mark.parametrize('data,uid', PUT_DATA)
    def test_put_item(self, get_remote_rest_utility, uid, data):
        """Test add a new item in the remote rest endpoint."""
        remote = get_remote_rest_utility
        result = remote.put(uid, data)
        assert isinstance(result, dict)
