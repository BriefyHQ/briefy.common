"""Colander schema types and validators."""
from colander import Invalid
from colander import null
from colander import SchemaType


class Dictionary(SchemaType):
    """A Dictionary schema type for colander."""

    def serialize(self, node, appstruct):
        """Serialize the schema type."""
        if appstruct is null or appstruct is None:
            return null
        elif not (isinstance(appstruct, dict)):
            raise Invalid(node, '{} is not a dict'.format(appstruct))
        return appstruct

    def deserialize(self, node, cstruct):
        """Deserialize the schema type."""
        return cstruct


class List(SchemaType):
    """A List schema type for colander."""

    def serialize(self, node, appstruct):
        """Serialize the schema type."""
        if appstruct is null or appstruct is None:
            return null
        elif not (isinstance(appstruct, list)):
            raise Invalid(node, '{} is not a list'.format(appstruct))
        return appstruct

    def deserialize(self, node, cstruct):
        """Deserialize the schema type."""
        return cstruct
