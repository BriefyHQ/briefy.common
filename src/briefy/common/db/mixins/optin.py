"""Opt in mixin."""
import sqlalchemy as sa


class OptIn:
    """A mixin providing optin information."""

    internal = sa.Column(sa.Boolean(), default=True)
    partners = sa.Column(sa.Boolean(), default=True)
