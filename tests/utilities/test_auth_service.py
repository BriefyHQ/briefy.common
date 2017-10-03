"""Test IAuthService utility"""
from briefy.common.utilities.interfaces import IAuthService
from briefy.common.utilities.interfaces import IRequestsAuthFactory
from zope.component import getUtility
from zope.interface import implementedBy
from zope.interface import providedBy

import pytest


@pytest.fixture(scope='module')
def get_auth_service_utility():
    """Fixture to create a new auth service utility instance."""
    utility = getUtility(IAuthService)
    return utility


@pytest.fixture(scope='module')
def get_requests_auth_factory_utility():
    """Fixture to get requests auth factory utility."""
    factory = getUtility(IRequestsAuthFactory)
    return factory


class TestAuthService:
    """Test auth service utility."""

    def test_get_utility(self, get_auth_service_utility):
        """Query utility and execute operations."""
        utility = get_auth_service_utility
        assert providedBy((utility, IAuthService))

    def test_login(self, get_auth_service_utility):
        """Test login operation."""
        utility = get_auth_service_utility
        token, user = utility.login()
        assert isinstance(token, str)
        assert isinstance(user, dict)


class TestRequestsAuthFactory:
    """Test requests auth factory utility."""

    def test_get_utility(self, get_requests_auth_factory_utility):
        """Query utility and execute operations."""
        factory = get_requests_auth_factory_utility
        assert implementedBy((factory, IRequestsAuthFactory))

    def test_call(self, get_requests_auth_factory_utility):
        """Test call operation."""
        factory = get_requests_auth_factory_utility

        class Request:
            """Mock request"""

            headers = {}

        request = Request()
        instance = factory()
        instance(request)
        assert 'Authorization' in request.headers
