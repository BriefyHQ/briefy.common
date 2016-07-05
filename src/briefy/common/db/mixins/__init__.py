"""Database mixins."""
from briefy.common.db.mixins.identifiable import GUID
from briefy.common.db.mixins.timestamp import Timestamp
from briefy.common.db.mixins.workflow import Workflow


class Mixin(GUID, Timestamp, Workflow):
    """Base mixin to be used for content classes on Briefy."""

    def __repr__(self):
        """Representation of this object."""
        return (
            """<{0}(id='{1}' state='{2}' created='{3}' updated='{4}')>""").format(
                self.__class__.__name__,
                self.id,
                self.state,
                self.created_at,
                self.updated_at
        )
