"""Item base model."""
from briefy.common.db import Base
from briefy.common.db.mixins import Mixin
from briefy.common.db.models.local_role import LocalRole
from briefy.common.log import logger
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.session import object_session

import sqlalchemy as sa
import uuid


class Item(Mixin, Base):
    """Model class to be used as base for all first class models."""

    __tablename__ = 'items'

    path = sa.Column(ARRAY(UUID(as_uuid=True)), nullable=False)
    """List of all parent objects including itself."""

    type = sa.Column(sa.String(50))
    """Polymorphic type."""

    @declared_attr
    def __mapper_args__(cls):
        """Return polymorphic identity."""
        cls_name = cls.__name__.lower()
        args = {
            'polymorphic_identity': cls_name,
        }
        if cls_name == 'item':
            args['polymorphic_on'] = cls.type
        return args

    local_roles = sa.orm.relationship(
        LocalRole,
        order_by='asc(LocalRole.created_at)',
        backref=sa.orm.backref('item'),
        lazy='noload'
    )

    @classmethod
    def get_expression(cls, role_name):
        """Get expression for a specific role name."""
        return sa.select([LocalRole.principal_id]).where(
            sa.and_(
                LocalRole.item_id == cls.id,
                LocalRole.role_name == role_name
            )
        ).as_scalar()

    @classmethod
    def create(cls, payload) -> object:
        """Factory that creates a new instance of this object.

        :param payload: Dictionary containing attributes and values
        :type payload: dict
        """
        actors_data = {
            actor: payload.pop(actor) for actor in cls.__actors__ if actor in payload
        }

        parent_id = payload.pop('parent_id', None)
        obj_id = payload.setdefault('id', uuid.uuid4())

        if parent_id:
            parent = Item.get(parent_id)
            path = parent.path
        else:
            path = []

        path.append(obj_id)
        payload['path'] = path

        obj = cls(**payload)
        obj.update(actors_data)
        return obj

    def principals_by_role(self, role_name):
        """Query principals with local roles in this Item."""
        return [role.principal_id for role in self.local_roles
                if role.role_name == role_name]

    def set_local_role(self, values: list, role_name: str):
        """Set local role collection."""
        current_users = set(getattr(self, role_name))
        updated_users = set(values)
        to_add = updated_users - current_users
        to_remove = current_users - updated_users
        session = object_session(self)

        if session and to_remove:
            # delete
            remove_roles = session.query(LocalRole).filter(
                LocalRole.role_name == role_name,
                LocalRole.principal_id.in_(to_remove),
                LocalRole.item_id == self.id
            )
            for lr in remove_roles:
                logger.debug('Deleted: {0}'.format(lr))
                session.delete(lr)

            session.flush()

        if session and to_add:
            # add
            for principal_id in to_add:
                lr = LocalRole(
                    item_id=self.id,
                    role_name=role_name,
                    principal_id=principal_id
                )
                session.add(lr)
                self.local_roles.append(lr)
                logger.debug('Added: {0}'.format(lr))

            session.flush()

    def __repr__(self) -> str:
        """Representation model Item."""
        template = "<{0}(id='{1}' state='{2}' created='{3}' updated='{4}' type='{5}')>"
        return template.format(
                self.__class__.__name__,
                self.id,
                self.state,
                self.created_at,
                self.updated_at,
                self.type
            )
