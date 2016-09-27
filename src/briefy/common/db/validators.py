"""Custom colander validators."""
import colander


class GeoJSONSchema(colander.MappingSchema):
    """GeoJSON Point schema validator."""

    type = colander.SchemaNode(colander.String())
    coordinates = colander.SchemaNode(colander.List())


class LocalityInfoSchema(colander.MappingSchema):
    """Locality info schema validator."""

    additional_info = colander.SchemaNode(colander.String())
    province = colander.SchemaNode(colander.String())
    locality = colander.SchemaNode(colander.String())
    sublocality = colander.SchemaNode(colander.String())
    route = colander.SchemaNode(colander.String())
    street_number = colander.SchemaNode(colander.String())
    country = colander.SchemaNode(colander.String())
    postal_code = colander.SchemaNode(colander.String())
