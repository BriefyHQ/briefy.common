"""External Integration mixins."""
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
    """Knack Integration mixin.

    It provides base information that is shared by all Knack-backed objects.
    """

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
    """External ID represents the ID of this object on Knack Database.

    i.e: 57dc4aca531d76010cba73c0
    """

    @declared_attr
    def _external_model_(cls) -> str:
        """Name of the model on Knack.

        Usually is the same name of our class, but in some cases we need to override this.
        i.e.: Professional on Leica is Photographer on Knack

        :returns: String with the name of this class on Knack.
        """
        return cls.__name__

    def get_knack_object(self):
        """Return the Knack object referenced here.

        :returns: An instance of :class:`briefy,knack.base.KnackEntity`
        """
        external_id = self.external_id
        if HAS_BRIDGE and external_id:
            KModel = K.get_model(self._external_model_)
            return KModel.get(self.external_id)
