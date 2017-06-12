"""UserProfileQuery tests."""
from briefy.common.users import SystemUser
from briefy.common.utilities.interfaces import IUserProfileQuery
from zope.component import getUtility


def test_user_profile_utility_get_data():
    """Check if the user profile utility is working."""
    profile_service = getUtility(IUserProfileQuery)
    result = profile_service.get_data(SystemUser.id)
    for key, value in result.items():
        assert value == getattr(SystemUser, key)


def test_user_profile_utility_state_history():
    """Check if the user profile utility is working."""
    profile_service = getUtility(IUserProfileQuery)
    state_history = [
        {
            'actor': SystemUser.id
        }
    ]
    results = profile_service.update_wf_history(state_history)
    for item in results:
        for key, value in item['actor'].items():
            assert value == getattr(SystemUser, key)
