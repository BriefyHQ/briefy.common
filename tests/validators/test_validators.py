"""Tests for `briefy.common.validators` package."""
import pytest


class DummySchemaNode:
    """Dummy Schema Node."""

    name = 'foo'


class TestEventNameValidator:
    """Test EventName validator."""

    def _validate(self, val):
        from briefy.common.validators import EventName
        return EventName(DummySchemaNode(), val)

    def test_successes(self):
        """Test validation successes."""
        assert self._validate('event.name') is None
        assert self._validate('event.name.surname') is None
        assert self._validate('event.name.surname.long') is None

    def test_failures(self):
        """Test validation failures."""
        from colander import Invalid
        values = [
            'not an event name',
            '1',
            'foo.bar.',
            '.foo.bar',
            'foo_bar',
        ]

        for val in values:
            with pytest.raises(Invalid) as excinfo:
                self._validate(val)
            assert 'Invalid event name' in str(excinfo.value)
