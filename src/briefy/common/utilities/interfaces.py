"""Interfaces definiton for all common services."""
from zope.interface import Interface


class IUserProfileQuery(Interface):
    """Utility that query user profile data based on the user id."""

    def get_data(user_id: str) -> dict:
        """Get a map with user data."""

    def update_wf_history(state_history: list) -> list:
        """Update workflow history with user data."""
