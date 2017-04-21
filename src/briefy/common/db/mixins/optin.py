"""Communication opt in mixin."""
import sqlalchemy as sa


class OptIn:
    """A mixin providing optin information."""

    internal = sa.Column(sa.Boolean(), default=True)
    """User accepts communication from Briefy."""

    partners = sa.Column(sa.Boolean(), default=True)
    """User accepts communication from Briefy partners."""
