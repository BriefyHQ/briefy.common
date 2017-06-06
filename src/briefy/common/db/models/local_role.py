"""LocalRole base model."""
from briefy.common.db.mixins import GUID
from briefy.common.db.mixins import Timestamp
from briefy.common.db.model import Base
from sqlalchemy.dialects.postgresql import UUID

import sqlalchemy as sa


class LocalRole(Timestamp, GUID, Base):
    """LocalRole model to store roles in context."""

    __tablename__ = 'localroles'

    item_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey('items.id'), nullable=False)
    """ID of the item object (context)"""

    principal_id = sa.Column(UUID(as_uuid=True), nullable=False)
    """ID of the principal (user or group) which have the role in this context."""

    role_name = sa.Column(sa.String(255), nullable=False)
    """Name of the role the permission granted."""

    def __repr__(self):
        """Representation of a LocalRole."""
        return 'LocalRole(item_id={0}, principal_id={1}, role_name={2})'.format(
            self.item_id,
            self.principal_id,
            self.role_name
        )


class LocalRoleDescriptor:
    """Descriptor to create and update local roles."""

    def __init__(self, role_name: str, session) -> None:
        """Initialize descriptor."""
        self.role_name = role_name
        self.session = session

    def __get__(self, obj, obj_type=None) -> list:
        """Get principal id from local role instance."""
        return obj.principal_id

    def __set__(self, obj, value: list) -> None:
        """Update the local roles."""
        pass

    def __delete__(self, obj):
        """Delete all items."""
        pass


class LocalRolesGetSetFactory:
    """Factory that return get and set functions to the AssociationProxy."""

    def __init__(self, role_name, session):
        """Initialize LocalRolesGetSetFactory."""
        self.role_name = role_name
        self.session = session

    def __call__(self, collection, proxy):
        """Create a new descriptor instance and return the set and get functions."""
        descriptor = LocalRoleDescriptor(
            self.role_name,
            self.session,
        )
        return descriptor.__get__, descriptor.__set__
