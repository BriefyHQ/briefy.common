"""LocalPermission base model."""
from briefy.common.db.mixins import GUID
from briefy.common.db.mixins import Timestamp
from briefy.common.db.model import Base
from sqlalchemy.dialects.postgresql import UUID

import sqlalchemy as sa


class LocalPermission(Timestamp, GUID, Base):
    """Local permission model to store permissions per role in the context."""

    __tablename__ = 'localpermissions'

    item_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey('items.id'), nullable=False)
    """ID of the item object (context)."""

    role_name = sa.Column(sa.String(255), nullable=False)
    """Name of the role the permission granted."""

    create = sa.Column(sa.Boolean, default=False, nullable=False)
    """Define if the user can create a new object in the context."""

    update = sa.Column(sa.Boolean, default=False, nullable=False)
    """Define if the user can update values in the object."""

    view = sa.Column(sa.Boolean, default=False, nullable=False)
    """Define if the user can view the object."""

    delete = sa.Column(sa.Boolean, default=False, nullable=False)
    """Define if the user can delete the object."""

    execute = sa.Column(sa.Boolean, default=False, nullable=False)
    """Define if the user can execute an operation in the object."""

    def __repr__(self):
        """Representation of a LocalPermission."""
        template = 'LocalPermission(item_id={0}, role_name={1}, create={2}, ' \
                   'update={3}, view={4}, delete={5}, execute={6})'
        return template.format(
                self.item_id,
                self.role_name,
                self.create,
                self.update,
                self.view,
                self.delete,
                self.execute,
            )
