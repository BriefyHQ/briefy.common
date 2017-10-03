"""Authentication functions to query api services."""
from briefy.common import config
from briefy.common.log import logger
from briefy.common.utilities.interfaces import IAuthService
from briefy.common.utilities.interfaces import IRequestsAuthFactory
from briefy.common.utils.cache import timeout_cache
from zope.component import getUtility
from zope.interface import implementer

import requests
import typing as t


@implementer(IRequestsAuthFactory)
class RequestsAuthFactory:
    """Utility to returns an instance of requests.auth.AuthBase."""

    token = None
    user = None

    def __call__(self, request):
        """Customized authentication for briefy API request."""
        if not self.token:
            service = getUtility(IAuthService)
            self.token, self.user = service.login()
        request.headers['Authorization'] = 'JWT {token}'.format(token=self.token)
        return request


@implementer(IAuthService)
class RolleiflexAuthService:
    """Auth service implementation that query briefy.rolleiflex and return the JWT token."""

    def headers(self):
        """Default headers for all API requests."""
        headers = {'X-Locale': 'en_GB',
                   'User-Agent': config.USER_AGENT}
        return headers

    @timeout_cache(config.LOGIN_TIMEOUT)
    def login(
            self,
            username:
            str=config.API_USERNAME,
            password: str=config.API_PASSWORD
    ) -> t.Tuple[str, dict]:
        """Use briefy.rolleiflex email login to get a valid token."""
        uri = config.LOGIN_ENDPOINT
        data = dict(username=username)
        if config.ENV == 'development' or 'internal' not in uri:
            data.update(password=password)
        logger.debug(f'Login on rolleiflex with username: {username} endpoint: {uri}')
        response = requests.post(uri, data=data, headers=self.headers())
        if response.status_code == 200:
            result = response.json()
            token = result.get('token')
            user = result.get('user')
            return token, user
        else:
            msg = response.text
            error = f'Login failed! payload: {data} endpoint: {uri} message: {msg}'
            logger.error(error)
            raise Exception(error)


def factory():
    """Create an instance of the IAuthService utility."""
    return RolleiflexAuthService()
