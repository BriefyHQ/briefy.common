"""Colander schema types and validators."""
from colander import Invalid
from colander import null
from colander import SchemaType


def validate_and_serialize(schema: colander.SchemaType, data: dict) -> dict:
    """Validate Python data using a colander schema.

    :param schema: Schema
    :param data: entity data
    :returns: Colaner serialized data
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


class List(SchemaType):
    """A List schema type for colander."""

    def serialize(self, node, appstruct):
        """Serialize the schema type."""
        if appstruct is null or appstruct is None:
            return None
        elif not (isinstance(appstruct, list)):
            raise Invalid(node, '{struct} is not a dict'.format(struct=appstruct))
        return appstruct

    def deserialize(self, node, cstruct):
        """Deserialize the schema type."""
        return cstruct
