"""Colander schema types and validators."""
from colander import Invalid
from colander import null
from colander import SchemaNode
from colander import SchemaType

import collections
import json
import typing as t


def validate_and_serialize(schema: SchemaType, data: dict) -> dict:
    """Validate Python data using a colander schema.

    :param schema: Schema
    :param data: entity data
    :returns: Colander serialized data
    :raises: `colander.Invalid`
    """
    # Colander only runs its validation on de-serialize
    value = schema.serialize(data)
    schema.deserialize(value)
    return value


class Dictionary(SchemaType):
    """A Dictionary schema type for colander."""

    def serialize(self, node: SchemaNode, appstruct: dict) -> t.Optional[dict]:
        """Serialize the schema type."""
        if appstruct is null or appstruct is None:
            return None
        elif not (isinstance(appstruct, dict)):
            raise Invalid(node, f'{appstruct} is not a dict')
        return appstruct

    def deserialize(self, node: SchemaNode, cstruct: dict) -> dict:
        """Deserialize the schema type."""
        return cstruct


class Coordinate(SchemaType):
    """New type to handle Coordinate field."""

    def serialize(self, node: SchemaNode, appstruct: dict) -> t.Optional[dict]:
        """Serialize the schema type."""
        if appstruct is null or appstruct is None:
            return None
        elif not (isinstance(appstruct, dict)):
            raise Invalid(node, f'{appstruct} is not a dict')
        return appstruct

    def deserialize(self, node: SchemaNode, cstruct: t.Sequence) -> dict:
        """Deserialize the schema type."""
        value = cstruct
        if isinstance(value, (list, tuple)):
            value = {
                'type': 'Point',
                'coordinates': [cstruct[1], cstruct[0]]
            }
        return value


class List(SchemaType):
    """A List schema type for colander."""

    def serialize(self, node: SchemaNode, appstruct: t.List) -> t.Optional[t.List]:
        """Serialize the schema type."""
        if appstruct is null or appstruct is None:
            return None
        elif not (isinstance(appstruct, list)):
            raise Invalid(node, f'{appstruct} is not a list')
        return appstruct

    def deserialize(self, node: SchemaNode, cstruct) -> t.List:
        """Deserialize the schema type."""
        return cstruct


class JSONType(SchemaType):
    """Colander type which is able to serialize and deserialize JSON."""

    def serialize(self, node: SchemaNode, appstruct: dict) -> t.Optional[str]:
        """Serialize JSON."""
        if appstruct is null:
            return None
        try:
            return json.dumps(appstruct)
        except Exception as exc:
            raise Invalid(node, f'{appstruct} cannot be serialized: {exc}')

    def deserialize(self, node: SchemaNode, cstruct: dict) -> t.Optional[dict]:
        """Deserialize JSON."""
        if cstruct is null:
            return None
        if isinstance(cstruct, dict):
            return cstruct
        try:
            # use OrderedDict as order is important for us.
            return json.loads(cstruct, object_pairs_hook=collections.OrderedDict)
        except Exception as exc:
            raise Invalid(node, f'{cstruct} is not a JSON object: {exc}')

    def cstruct_children(self, node: SchemaNode, cstruct: dict) -> t.List:
        """Used to determine the children of this type.

        As deserializing JSON also makes sure the children are correct
        we do not use this system.
        """
        return []
