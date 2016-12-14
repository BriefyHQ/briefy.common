"""Tests for `briefy.common.utils.data` module."""
from briefy.common.utils import data

import pytest


testdata = [
    ('Foo', 'foo'),
    ('Foo bar', 'foo-bar'),
    ('Berlin', 'berlin'),
    (' Berlin', 'berlin'),
    (' Berlin  ', 'berlin'),
    (' Fußball  ', 'fussball'),
    (' Briefy Project in Münch  ', 'briefy-project-in-munch'),
]


@pytest.mark.parametrize("value,expected", testdata)
def test_generate_slug(value, expected):
    """Test generate_slug."""
    func = data.generate_slug
    assert func(value) == expected


testdata = [
    ({'id': '1234567890', 'title': 'Berlin'}, '12345678-berlin'),
    ({'id': '1234567890', 'title': 'Fußball'}, '12345678-fussball'),
    ({'id': '', 'title': ''}, ''),
    ({'id': None, 'title': None}, ''),
    ({'id': None, 'title': 'Fußball'}, 'fussball'),
    ({'id': '1234567890', 'title': None}, '12345678'),
    ({'id': 12345, 'title': None}, '12345'),
]


@pytest.mark.parametrize("value,expected", testdata)
def test_generate_contextual_slug(value, expected):
    """Test generate_contextual_slug."""
    func = data.generate_contextual_slug
    assert func(value) == expected
