"""Interfaces definiton for all common services."""
from zope.interface import Interface

import requests
import typing as t


class IUserProfileQuery(Interface):
    """Utility that query user profile data based on the user id."""

    def get_data(user_id: str) -> dict:
        """Get a map with user data."""

    def update_wf_history(state_history: list) -> list:
        """Update workflow history with user data."""


class IAuthService(Interface):
    """Utility to get a JWT token from rolleiflex service."""

    def login(self, username, password) -> t.Tuple[str, dict]:
        """Login to the external service and return a JWT token and user payload."""


class IRequestsAuthFactory(Interface):
    """Utility to get an instance of requests.auth.AuthBase implementation."""

    def __call__(self, remote) -> requests.auth.AuthBase:
        """Return an instance of requests.auth.AuthBase that knows how to get the auth header."""


class IRemoteRestEndpoint(Interface):
    """Remote endpoint factory to get, post, put and delete items."""

    def __init__(base_uri: str, base_path: str, name: str):
        """Initialize the utility to get an specifc REST endpoint."""

    def post(data: dict):
        """Post a new item to the service endpoint with the data payload."""

    def get(uid: str):
        """Get and item from service endpoint based in the uid."""

    def put(uid: str, data: dict):
        """Update un item in the service endpoint based in the uid."""
