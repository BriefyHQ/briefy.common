"""Tests for `briefy.common.utils.schema` package."""
from briefy.common.utils import schema

import colander
import pytest


class DummySchemaNode:
    """Dummy Schema Node."""

    def __init__(self, typ, name='', exc=None, default=None):
        """Initialize."""
        self.typ = typ
        self.name = name
        self.exc = exc
        self.required = default is None
        self.default = default
        self.children = []

    def deserialize(self, val):
        """Deserialize."""
        from colander import Invalid
        if self.exc:
            raise Invalid(self, self.exc)
        return val

    def serialize(self, val):
        """Serialize."""
        from colander import Invalid
        if self.exc:
            raise Invalid(self, self.exc)
        return val

    def __getitem__(self, name):
        """Get item."""
        for child in self.children:
            if child.name == name:
                return child


class TestDictionary:
    """Tests for Dictionary schema type."""

    def _makeOne(self):
        return schema.Dictionary()

    def test_serialize_dict(self):
        """Test serialization of a dictionary."""
        schema = self._makeOne()
        appstruct = {'foo': 'bar'}
        assert schema.serialize(DummySchemaNode(None), appstruct) == appstruct

    def test_deserialize_dict(self):
        """Test deserialization of a dictionary."""
        schema = self._makeOne()
        cstruct = {'foo': 'bar'}
        assert schema.deserialize(DummySchemaNode(None), cstruct) == cstruct

    def test_serialize_none_value(self):
        """Test serialization of None."""
        schema = self._makeOne()
        appstruct = colander.null
        assert schema.serialize(DummySchemaNode(None), appstruct) == appstruct
        assert schema.serialize(DummySchemaNode(None), None) == appstruct

    def test_serialize_wrong_value(self):
        """Test serialization of wrong types."""
        schema = self._makeOne()
        appstruct = 1
        with pytest.raises(colander.Invalid) as excinfo:
            schema.serialize(DummySchemaNode(None), appstruct)

        assert '1 is not a dict' in str(excinfo.value)

        appstruct = 'foo'
        with pytest.raises(colander.Invalid) as excinfo:
            schema.serialize(DummySchemaNode(None), appstruct)

        assert 'foo is not a dict' in str(excinfo.value)

        appstruct = 2.3
        with pytest.raises(colander.Invalid) as excinfo:
            schema.serialize(DummySchemaNode(None), appstruct)

        assert '2.3 is not a dict' in str(excinfo.value)


class TestList:
    """Tests for List schema type."""

    def _makeOne(self):
        return schema.List()

    def test_serialize_list(self):
        """Test serialization of a list."""
        schema = self._makeOne()
        appstruct = ['foo', 'bar']
        assert schema.serialize(DummySchemaNode(None), appstruct) == appstruct

    def test_deserialize_dict(self):
        """Test deserialization of a dictionary."""
        schema = self._makeOne()
        cstruct = ['foo', 'bar']
        assert schema.deserialize(DummySchemaNode(None), cstruct) == cstruct

    def test_serialize_none_value(self):
        """Test serialization of None."""
        schema = self._makeOne()
        appstruct = colander.null
        assert schema.serialize(DummySchemaNode(None), appstruct) == appstruct
        assert schema.serialize(DummySchemaNode(None), None) == appstruct

    def test_serialize_wrong_value(self):
        """Test serialization of wrong types."""
        schema = self._makeOne()
        appstruct = 1
        with pytest.raises(colander.Invalid) as excinfo:
            schema.serialize(DummySchemaNode(None), appstruct)

        assert '1 is not a list' in str(excinfo.value)

        appstruct = 'foo'
        with pytest.raises(colander.Invalid) as excinfo:
            schema.serialize(DummySchemaNode(None), appstruct)

        assert 'foo is not a list' in str(excinfo.value)

        appstruct = 2.3
        with pytest.raises(colander.Invalid) as excinfo:
            schema.serialize(DummySchemaNode(None), appstruct)

        assert '2.3 is not a list' in str(excinfo.value)
