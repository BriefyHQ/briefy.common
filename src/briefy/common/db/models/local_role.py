"""LocalRole base model."""
from briefy.common.db.mixins import Identifiable
from briefy.common.db.mixins import Timestamp
from briefy.common.db.model import Base
from sqlalchemy.dialects.postgresql import UUID

import colander
import sqlalchemy as sa


class LocalRole(Timestamp, Identifiable, Base):
    """LocalRole model to store roles in context."""

    __tablename__ = 'localroles'

    item_type = sa.Column(
        sa.String(255),
        index=True,
        nullable=False
    )
    """Item type.

    Name of the entity -- as in its class name.
    """

    item_id = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey('items.id'),
        index=True,
        nullable=False,
        info={
            'colanderalchemy': {
                'title': 'Item UUID',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """ID of the item object (context)"""

    principal_id = sa.Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Principal UUID',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """ID of the principal (user or group) which have the role in this context."""

    role_name = sa.Column(sa.String(255), nullable=False, index=True)
    """Name of the role the permission granted."""

    def __repr__(self) -> str:
        """Representation of a LocalRole."""
        return 'LocalRole(item_id={0}, principal_id={1}, role_name={2})'.format(
            self.item_id,
            self.principal_id,
            self.role_name
        )
