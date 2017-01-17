"""Colander schema types and validators."""
from colander import Invalid
from colander import null
from colander import SchemaType

import collections
import json


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

    def serialize(self, node, appstruct):
        """Serialize the schema type."""
        if appstruct is null or appstruct is None:
            return None
        elif not (isinstance(appstruct, dict)):
            raise Invalid(node, '{struct} is not a dict'.format(struct=appstruct))
        return appstruct

    def deserialize(self, node, cstruct):
        """Deserialize the schema type."""
        return cstruct


class Coordinate(SchemaType):
    """New type to handle Coordinate field."""

    def serialize(self, node, appstruct):
        """Serialize the schema type."""
        if appstruct is null or appstruct is None:
            return None
        elif not (isinstance(appstruct, dict)):
            raise Invalid(node, '{struct} is not a dict'.format(struct=appstruct))
        return appstruct

    def deserialize(self, node, cstruct):
        """Deserialize the schema type."""
        value = cstruct
        if isinstance(value, (list, tuple)):
            value = {
                'type': 'Point',
                'coordinates': [cstruct[0], cstruct[1]]
            }
        return value


class List(SchemaType):
    """A List schema type for colander."""

    def serialize(self, node, appstruct):
        """Serialize the schema type."""
        if appstruct is null or appstruct is None:
            return None
        elif not (isinstance(appstruct, list)):
            raise Invalid(node, '{struct} is not a list'.format(struct=appstruct))
        return appstruct

    def deserialize(self, node, cstruct):
        """Deserialize the schema type."""
        return cstruct


class JSONType(SchemaType):
    """Colander type which is able to serialize and deserialize JSON."""

    def serialize(self, node, appstruct):
        """Serialize JSON."""
        if appstruct is null:
            return null
        try:
            return json.dumps(appstruct)
        except Exception as e:
            raise Invalid(node, '{0} cannot be serialized: {1}'.format(appstruct, e))

    def deserialize(self, node, cstruct):
        """Deserialize JSON."""
        if cstruct is null:
            return null
        if isinstance(cstruct, dict):
            return cstruct
        try:
            # use OrderedDict as order is important for us.
            return json.loads(cstruct, object_pairs_hook=collections.OrderedDict)
        except Exception as e:
            raise Invalid(node, '{0} is not a JSON object: {1}'.format(cstruct, e))

    def cstruct_children(self, node, cstruct):
        """Used to determine the children of this type.

        As deserializing JSON also makes sure the children are correct
        we do not use this system.
        """
        return []
