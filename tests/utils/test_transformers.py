"""Tests for `briefy.common.utils.transformers` module."""
from briefy.common.utils.transformers import json_dumps


class TestJsonDumps:
    """Tests for json_dumps."""

    def test_serialize_date(self):
        """Test serialization of a date object."""
        from datetime import date

        value = date(2012, 3, 29)
        expected = '"2012-03-29T00:00:00"'
        assert json_dumps(value) == expected

    def test_serialize_datetime(self):
        """Test serialization of a datetime object."""
        from datetime import datetime

        value = datetime(2012, 3, 29, 12, 31, 22)
        expected = '"2012-03-29T12:31:22Z"'
        assert json_dumps(value) == expected

    def test_serialize_time(self):
        """Test serialization of a time object."""
        from datetime import time

        value = time(12, 31, 22)
        expected = '"12:31:22"'
        assert json_dumps(value) == expected

    def test_serialize_decimal(self):
        """Test serialization of a decimal object."""
        from decimal import Decimal

        value = Decimal('2.35')
        expected = '"2.35"'
        assert json_dumps(value) == expected

    def test_serialize_colander_null(self):
        """Test serialization of a colander.null."""
        import colander

        value = colander.null
        expected = 'null'
        assert json_dumps(value) == expected

    def test_serialize_default(self):
        """Test serialization of default object."""
        value = 2
        expected = '2'
        assert json_dumps(value) == expected

        value = 'Foo'
        expected = '"Foo"'
        assert json_dumps(value) == expected

        value = ['Foo', ]
        expected = '["Foo"]'
        assert json_dumps(value) == expected
