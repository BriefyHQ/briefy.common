"""Tests for `briefy.common.utils.phone` module."""
from briefy.common.utils import phone

import pytest


test_data = [
    ('+5511984443867', True),
    ('+55(11)98444-3867', True),
    ('+4917637755722', True),
    ('+1 805 825 7461', True),
    ('+4930609898232', True),
    ('004930609898232', False),
    ('5511984443867', False),
    ('', False),
    (None, False),
]


@pytest.mark.parametrize('value,expected', test_data)
def test_validate_phone(value, expected):
    """Test validate_phone."""
    func = phone.validate_phone
    assert func(value) == expected
