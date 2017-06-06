"""Database mixins."""
from briefy.common.db.mixins.address import Address
from briefy.common.db.mixins.asset import Image  # noQA
from briefy.common.db.mixins.asset import ImageMixin  # noQA
from briefy.common.db.mixins.asset import ThreeSixtyImage  # noQA
from briefy.common.db.mixins.asset import ThreeSixtyImageMixin  # noQA
from briefy.common.db.mixins.asset import Video  # noQA
from briefy.common.db.mixins.asset import VideoMixin  # noQA
from briefy.common.db.mixins.external import KnackMixin  # noQA
from briefy.common.db.mixins.identifiable import GUID
from briefy.common.db.mixins.identifiable import GUIDFK
from briefy.common.db.mixins.metadata import BaseMetadata  # noQA
from briefy.common.db.mixins.metadata import BaseMetadata  # noQA
from briefy.common.db.mixins.person import ContactInfoMixin  # noQA
from briefy.common.db.mixins.person import NameMixin  # noQA
from briefy.common.db.mixins.person import PersonalInfoMixin  # noQA
from briefy.common.db.mixins.optin import OptIn  # noQA
from briefy.common.db.mixins.timestamp import Timestamp
from briefy.common.db.mixins.workflow import Workflow


class Mixin(GUID, Timestamp, Workflow):
    """Base mixin to be used for content classes on Briefy.

    Important: Always add Mixin as a base class _before_ the
    SQLAlchemy instrumented Base model - to warrant that any cooperative methods
    in the mixins are actually called.
    """

    def __repr__(self) -> str:
        """Representation of this object."""
        return (
            """<{0}(id='{1}' state='{2}' created='{3}' updated='{4}')>""").format(
                self.__class__.__name__,
                self.id,
                self.state,
                self.created_at,
                self.updated_at
        )


class SubItemMixin(GUIDFK, Timestamp, Workflow):
    """Item mixin to be used for content classes on Briefy.

    Important: Always add Mixin as a base class _before_ the
    SQLAlchemy instrumented Base model - to warrant that any cooperative methods
    in the mixins are actually called.
    """

    def __repr__(self) -> str:
        """Representation of this object."""
        return (
            """<{0}(id='{1}' state='{2}' created='{3}' updated='{4}')>""").format(
                self.__class__.__name__,
                self.id,
                self.state,
                self.created_at,
                self.updated_at,
        )


class AddressMixin(Address, Mixin):
    """Base Address mixin.

    Aggregates the following mixins:

        * :class:`briefy.common.db.mixins.Mixin` and
        * :class:`briefy.common.db.mixins.address.Address`

    """
