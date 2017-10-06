"""Remote Service utility."""
from briefy.common import config
from briefy.common.log import logger
from briefy.common.utilities.interfaces import IRemoteRestEndpoint
from briefy.common.utilities.interfaces import IRequestsAuthFactory
from zope.component import getUtility
from zope.interface import implementer

import json
import requests


@implementer(IRemoteRestEndpoint)
class RemoteRestEndpoint:
    """Remote endpoint component."""

    def __init__(self, base_uri, base_path, name):
        """Initilize remote endpoint utility."""
        self.base_path = base_path
        self.name = name
        self.base_uri = base_uri
        self.absolute_url = f'{base_uri}/{base_path}'

    def _requests_kwargs(self, data: dict=None):
        """Create lib requests base kwargs parameters."""
        headers = self.headers()
        auth = getUtility(IRequestsAuthFactory)()
        kwargs = {
            'headers': headers,
            'auth': auth
        }
        if data:
            kwargs['data'] = json.dumps(data)
        return kwargs

    def headers(self):
        """Return base headers."""
        """Default headers for all API requests."""
        headers = {'X-Locale': 'en_GB',
                   'User-Agent': config.USER_AGENT}
        return headers

    def post(self, data: dict) -> dict:
        """Update remote item."""
        uri = f'{self.absolute_url}/'
        name = self.name
        logger.info(f'Add item in {name}: {uri}')
        kwargs = self._requests_kwargs(data)
        response = requests.post(uri, **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            response = response.text
            error_msg = f'Fail to add item in {name}: {uri}. Response: {response}'
            logger.exception(error_msg)
            raise RuntimeError(error_msg)

    def put(self, uid: str, data: dict) -> dict:
        """Update remote item."""
        uri = f'{self.absolute_url}/{uid}'
        name = self.name
        logger.info(f'Updating item in {name}: {uri}')
        kwargs = self._requests_kwargs(data)
        response = requests.put(uri, **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            response = response.text
            error_msg = f'Fail to update item in {name}: {uri}. Response: {response}'
            logger.exception(error_msg)
            raise RuntimeError(error_msg)

    def get(self, uid: str) -> dict:
        """Get remote item."""
        uri = f'{self.absolute_url}/{uid}'
        name = self.name
        logger.info(f'Get item from {name}: {uri}')
        kwargs = self._requests_kwargs()
        response = requests.get(uri, **kwargs)
        if response.status_code == 200:
            data = response.json()
            return data
        elif response.status_code == 404:
            return None
        else:
            response = response.text
            error_msg = f'Fail to get item from {name}: {uri}. Response: {response}'
            logger.exception(error_msg)
            raise RuntimeError(error_msg)

    def query(self, payload: dict=None, items_per_page=25) -> dict:
        """Get items using key:value payload as filter and number of results per page."""
        uri = f'{self.absolute_url}'
        name = self.name
        logger.info(f'Listing items from {name}: {uri}')
        kwargs = self._requests_kwargs()
        if not payload:
            payload = {}

        payload['_items_per_page'] = items_per_page
        kwargs['params'] = payload
        response = requests.get(uri, **kwargs)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            response = response.text
            error_msg = f'Fail list items from {name}: {uri}. Response: {response}'
            logger.exception(error_msg)
            raise RuntimeError(error_msg)
