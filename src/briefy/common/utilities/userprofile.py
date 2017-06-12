"""UserProfileData service."""
from briefy.common.log import logger
from briefy.common.users import SystemUser
from briefy.common.utilities.interfaces import IUserProfileQuery
from uuid import UUID
from zope.interface import implementer


@implementer(IUserProfileQuery)
class BaseUserProfileQuery:
    """Stub implementation of the IUserProfileQuery interface."""

    def get_data(self, user_id: str) -> dict:
        """Get a map with user data."""
        data = {
            'id': str(user_id),
            'first_name': '',
            'last_name': '',
            'fullname': '',
            'email': '',
            'internal': False,
        }
        try:
            _ = UUID(user_id)  # noQA
        except (ValueError, AttributeError):
            logger.error(f'Actor id is not a valid UUID: {user_id}')
        else:
            if user_id == SystemUser.id:
                raw_data = SystemUser
                data['first_name'] = raw_data.first_name
                data['last_name'] = raw_data.last_name
                data['fullname'] = raw_data.title
                data['email'] = raw_data.email
                data['internal'] = raw_data.internal

        return data

    def update_wf_history(self, state_history: list) -> list:
        """Update workflow history with user data."""
        for item in state_history:
            user = item.get('actor', None)
            # first call when the actor value still a UUID string
            if isinstance(user, str):
                user_id = user
                new_actor = self.get_data(user_id)
                if new_actor:
                    item['actor'] = new_actor

        return state_history


def get_user_profile_service():
    """Create a new instance of IUserProfileQuery service."""
    return BaseUserProfileQuery()
