"""Mixin for versioned models."""
from sqlalchemy_continuum.utils import count_versions


class VersionMixin:
    """Versioning mixin."""

    __versioned__ = {
        'exclude': ['state_history', '_state_history', ]
    }
    """SQLAlchemy Continuum settings.

    By default we do not keep track of state_history.
    """

    @property
    def version(self) -> int:
        """Return the current version number.

        We are civilised here, so version numbering starts from zero ;-)
        :return: Version number of this object.
        """
        versions = count_versions(self)
        return versions - 1

    @version.setter
    def version(self, value: int) -> int:
        """Explicitly sets a version to the asset (Deprecated).

        XXX: Here only to avoid issues if any client tries to set this.
        :param value:
        """
        pass
