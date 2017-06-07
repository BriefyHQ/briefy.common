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