"""Personal information mixin."""
from sqlalchemy.ext.hybrid import hybrid_property

import sqlalchemy as sa


class NameMixin:
    """A mixin to handle name information."""

    first_name = sa.Column(sa.String(255), nullable=False, unique=False)
    last_name = sa.Column(sa.String(255), nullable=False, unique=False)
    display_name = sa.Column(sa.String(255), nullable=True, unique=False)

    @hybrid_property
    def fullname(self):
        """Fullname of this person."""
        return '{first_name} {last_name}'.format(
            first_name=self.first_name,
            last_name=self.last_name,
        )