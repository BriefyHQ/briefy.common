"""Item base model."""
from briefy.common.db import Base
from briefy.common.db.mixins import Mixin
from briefy.common.db.models.local_role import LocalRole
from briefy.common.log import logger
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.session import object_session

import sqlalchemy as sa


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
        lazy='dynamic'
    )

    @classmethod
    def create_lr_relationship(cls, role_name, uselist=True):
        """Create LocalRole relationship for a specific role name."""
        return sa.orm.relationship(
            'LocalRole',
            uselist=uselist,
            lazy='noload',
            foreign_keys='LocalRole.item_id',
            primaryjoin="""and_(
                    LocalRole.item_id==Item.id,
                    LocalRole.role_name=="{role_name}"
                )""".format(
                role_name=role_name
            )
        )

    @classmethod
    def create_local_role(cls, principal_id, role_name, item_id=None):
        """Create local LocalRole instance for role and user_id."""
        if not item_id:
            item_id = cls.id

        payload = dict(
            item_id=item_id,
            principal_id=principal_id,
            role_name=role_name,
        )
        return LocalRole(**payload)

    @classmethod
    def create_lr_proxy(cls, role_name, local_attr=None):
        """Get a new association proxy instance."""
        if not local_attr:
            local_attr = '_{role_name}'.format(role_name=role_name)

        def creator(principal_id):
            """Create a new local role instance."""
            return cls.create_local_role(principal_id, role_name)

        return association_proxy(
            local_attr,
            'principal_id',
            creator=creator
        )

    def principals_by_role(self, role_name):
        """Query principals with local roles in this Item."""
        session = object_session(self)
        local_roles = session.query(LocalRole).filter(
            LocalRole.role_name == role_name,
            LocalRole.item_id == self.id
        )
        return [role.principal_id for role in local_roles]

    def set_local_role(self, values: list, role_name: str):
        """Set local role collection."""
        current_users = set(getattr(self, role_name))
        updated_users = set(values)
        to_add = updated_users - current_users
        to_remove = current_users - updated_users
        session = object_session(self)

        # delete
        remove_roles = session.query(LocalRole).filter(
            LocalRole.role_name == role_name,
            LocalRole.principal_id.in_(to_remove),
            LocalRole.item_id == self.id
        )
        for lr in remove_roles:
            logger.debug('Deleted: {0}'.format(lr))
            session.delete(lr)

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
