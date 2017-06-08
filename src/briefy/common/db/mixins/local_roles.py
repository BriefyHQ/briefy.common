"""Local Roles mixin."""
from briefy.common.log import logger
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session

import sqlalchemy as sa


def get_lr_expression(cls, role_name):
    """Get expression for a specific role name."""
    from briefy.common.db.models.local_role import LocalRole
    return sa.select([LocalRole.principal_id]).where(
        sa.and_(
            LocalRole.item_id == cls.id,
            LocalRole.role_name == role_name
        )
    ).as_scalar()


def principals_by_role(obj, role_name):
    """Query principals with local roles in this Item."""
    return [role.principal_id for role in obj.local_roles
            if role.role_name == role_name]


def set_local_role(obj, values: list, role_name: str):
    """Set local role collection."""
    from briefy.common.db.models.local_role import LocalRole
    current_users = set(getattr(obj, role_name))
    updated_users = set(values)
    to_add = updated_users - current_users
    to_remove = current_users - updated_users
    session = object_session(obj)

    if session and to_remove:
        # delete
        remove_roles = session.query(LocalRole).filter(
            LocalRole.role_name == role_name,
            LocalRole.principal_id.in_(to_remove),
            LocalRole.item_id == obj.id
        )
        for lr in remove_roles:
            logger.debug('Deleted: {0}'.format(lr))
            session.delete(lr)

        session.flush()

    if session and to_add:
        # add
        for principal_id in to_add:
            lr = LocalRole(
                item_id=obj.id,
                role_name=role_name,
                principal_id=principal_id
            )
            session.add(lr)
            obj.local_roles.append(lr)
            logger.debug('Added: {0}'.format(lr))

        session.flush()


def make_lr_attr(actor):
    """Create local role hybrid_property attributes."""
    def getter(self):
        """Return the list of user_ids with a local role."""
        return principals_by_role(self, actor)

    def setter(self, values):
        """Update local role collection."""
        set_local_role(self, values, role_name=actor)

    def expression(cls):
        """Expression that return principal ids from database."""
        return get_lr_expression(cls, actor)

    lr_attr = hybrid_property(getter)
    lr_attr.setter(setter)
    lr_attr.expression(expression)
    return lr_attr


class LocalRolesMixin:
    """A mixin providing Local role support for an object."""

    __actors__ = ()

    def __init_subclass__(cls):
        """Initialize local roles in the cls."""
        for actor in cls.__actors__:
            setattr(cls, actor, make_lr_attr(actor))

    can_view = sa.Column(ARRAY(sa.String()), default=[], nullable=False)
    """List of local roles that can view an item."""

    @declared_attr
    def local_roles(self):
        """Local roles relationship."""
        return relationship(
            'LocalRole',
            order_by='asc(LocalRole.created_at)',
            backref=sa.orm.backref('item'),
            lazy='noload'
        )
