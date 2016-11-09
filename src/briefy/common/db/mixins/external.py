"""Knack Mixin."""
from sqlalchemy.ext.declarative import declared_attr

import colander
import pkg_resources
import sqlalchemy as sa

try:
    pkg_resources.get_distribution('briefy.knack')
except pkg_resources.DistributionNotFound:
    HAS_BRIDGE = False
else:
    HAS_BRIDGE = True
    import briefy.knack as K


class KnackMixin:
    """A mixin to deal with Knack."""

    external_id = sa.Column(
        sa.String,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'External ID',
                'missing': colander.drop
            }
        }
    )

    @declared_attr
    def _external_model_(cls):
        """Name of the model on Knack."""
        return cls.__name__

    def get_knack_object(self):
        """Return the Knack object referenced here."""
        external_id = self.external_id
        if HAS_BRIDGE and external_id:
            KModel = K.get_model(self._external_model_)
            return KModel.get(self.external_id)
