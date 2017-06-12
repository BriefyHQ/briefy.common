"""System users."""
from briefy.common.types import BaseUser


SystemUser = BaseUser(
    user_id='be319e15-d256-4587-a871-c3476affa309',
    data={
        'locale': 'en_GB',
        'fullname': 'Briefy',
        'first_name': 'Briefy',
        'last_name': '',
        'email': 'app@briefy.co',
        'groups': ['g:system', ],
        'title': 'Briefy'
    }
)
"""A Hard-coded System User to be used by other Briefy systems."""
