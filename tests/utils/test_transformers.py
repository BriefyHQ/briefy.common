"""Tests for `briefy.common.utils.transformers` module."""
from briefy.common.utils.transformers import json_dumps
from briefy.common.vocabularies.person import GenderCategories
from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal

import colander
import pytest
import pytz


testdata = [
    (date(2012, 3, 29), '"2012-03-29T00:00:00"'),
    (datetime(2012, 3, 29, 12, 31, 22, tzinfo=pytz.timezone('UTC')), '"2012-03-29T12:31:22+00:00"'),
    (time(12, 31, 22), '"12:31:22"'),
    (Decimal('2.35'), '"2.35"'),
    (colander.null, 'null'),
    (2.2, '2.2'),
    (2, '2'),
    ('Foo', '"Foo"'),
    (['Foo', ], '["Foo"]'),
    (GenderCategories.m, '"m"'),
    (GenderCategories.f, '"f"'),
]


@pytest.mark.parametrize('value,expected', testdata)
def test_serialize(value, expected):
    """Test serialization of am object."""
    assert json_dumps(value) == expected
