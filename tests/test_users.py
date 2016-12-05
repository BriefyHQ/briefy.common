"""Tests for `briefy.common.users` module."""
from briefy.common import users


def test_system_user():
    """Test System User implementation."""
    user = users.SystemUser
    assert user.id == 'be319e15-d256-4587-a871-c3476affa309'
    assert 'g:system' in user.groups
    assert user.email == 'app@briefy.co'
    assert user.fullname == 'Briefy'
