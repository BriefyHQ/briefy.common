"""Geoalchemy type specializations."""
from geoalchemy2 import Geography


class POINT(Geography):
    """A point data type initialized from a GeoJSON Object."""

    from_text = 'ST_GeomFromGeoJSON'

    def __init__(
            self, geometry_type='POINT', srid=4326, dimension=2, spatial_index=True, management=False
    ):
        """Initialize the type, make sure the geometry type is a POINT."""
        super().__init__('POINT', srid, dimension, spatial_index, management)
