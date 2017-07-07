"""Local Roles mixin."""
from briefy.common.log import logger
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import object_session

import colander
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

    current_users_list = getattr(obj, role_name)
    current_users = set(current_users_list)
    updated_users = set(values)
    to_add = updated_users - current_users
    to_remove = current_users - updated_users
    session = object_session(obj) or obj.__class__.__session__

    if session and to_remove:
        # delete
        to_remove_lr = [
            lr for lr in obj.local_roles
            if lr.principal_id in to_remove and lr.role_name == role_name
        ]
        for lr in to_remove_lr:
            logger.debug('Deleted: {0}'.format(lr))
            obj.local_roles.remove(lr)
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

    def __init_subclass__(cls, *args, **kwargs):
        """Initialize local roles in the subclass."""
        super().__init_subclass__(*args, **kwargs)
        for actor in cls.__actors__:
            setattr(cls, actor, make_lr_attr(actor))

    @classmethod
    def query(cls, principal_id=None, permission='can_view') -> Query:
        """Return query object.

        :returns: A query object
        """
        from briefy.common.db.models.local_role import LocalRole

        query = cls.__session__.query(cls)
        permission_attr = getattr(cls, permission)
        if principal_id:
            query = query.join(
                LocalRole, LocalRole.item_id == sa.any_(cls.path)
            ).filter(
                sa.and_(
                    LocalRole.principal_id == principal_id,
                    LocalRole.role_name == sa.any_(permission_attr),
                )
            )
        return query

    can_view = sa.Column(
        ARRAY(sa.String()),
        default=[],
        nullable=False,
        info={
            'colanderalchemy': {
                'title': 'Can view list',
                'missing': colander.drop,
                'typ': colander.List
            }
        }
    )
    """List of local roles that can view an item."""

    @declared_attr
    def local_roles(cls):
        """Local roles relationship."""
        return relationship(
            'LocalRole',
            foreign_keys='LocalRole.item_id',
            primaryjoin=f'LocalRole.item_id=={cls.__name__}.id',
            order_by='asc(LocalRole.created_at)',
            cascade='all, delete-orphan',
            info={
                'colanderalchemy': {
                    'title': 'Local Roles',
                    'missing': colander.drop,
                }
            }
        )
