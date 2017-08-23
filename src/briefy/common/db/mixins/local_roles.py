"""Local Roles mixin."""
from briefy.common import db
from briefy.common.db.comparator import BaseComparator
from briefy.common.log import logger
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import object_session
from uuid import UUID

import colander
import sqlalchemy as sa
import typing as t


ItemType = 'db.models.Item'
LocalRoleType = 'db.models.LocalRole'
ClassItemType = t.ClassVar['db.models.Item']
PrincipalIdType = t.TypeVar('PrincipalIdType', str, UUID)


def get_lr_expression(cls: ClassItemType, role_name: str) -> t.Sequence[UUID]:
    """Get expression for a specific role name."""
    from briefy.common.db.models.local_role import LocalRole

    return sa.select([LocalRole.principal_id]).where(
        sa.and_(
            LocalRole.item_id == cls.id,
            LocalRole.role_name == role_name
        )
    ).as_scalar()


def principals_by_role(obj: ItemType, role_name: str) -> t.List[str]:
    """Query principals with local roles in this Item."""
    return [role.principal_id for role in obj.local_roles
            if role.role_name == role_name]


def add_local_role(session: db.Session, obj: object, role_name: str, principal_id: PrincipalIdType):
    """Add new local role."""
    from briefy.common.db.models.local_role import LocalRole
    payload = dict(
        item_type=obj.__class__.__name__.lower(),
        item_id=obj.id,
        role_name=role_name,
        principal_id=principal_id
    )
    lr = LocalRole.create(payload)
    session.add(lr)
    obj.local_roles.append(lr)
    logger.debug('Added: {0}'.format(lr))


def del_local_role(session: db.Session, obj: ItemType, lr: LocalRoleType):
    """Delete existing local role."""
    obj.local_roles.remove(lr)
    session.delete(lr)
    logger.debug('Deleted: {0}'.format(lr))


def set_local_roles_by_role_name(
        obj: ItemType,
        role_name: str,
        principal_ids: t.List[PrincipalIdType]
):
    """Set local role collection: for one role set all users."""
    current_users_list = getattr(obj, role_name)
    current_users = set(current_users_list)
    updated_users = set(principal_ids)
    to_add = updated_users - current_users
    to_remove = current_users - updated_users
    session = object_session(obj) or obj.__session__

    if session and to_remove:
        to_remove_lr = [
            lr for lr in obj.local_roles
            if lr.principal_id in to_remove and lr.role_name == role_name
        ]
        for lr in to_remove_lr:
            del_local_role(session, obj, lr)
        session.flush()

    if session and to_add:
        for principal_id in to_add:
            add_local_role(session, obj, role_name, principal_id)
        session.flush()


def set_local_roles_by_principal(
        obj: ItemType,
        principal_id: PrincipalIdType,
        role_names: t.Sequence[str]
):
    """Set local role collection: for one role set all users."""
    current_roles = {r.role_name for r in obj.local_roles
                     if str(r.principal_id) == str(principal_id)}
    new_roles = set(role_names)
    to_add = new_roles - current_roles
    to_remove = current_roles - new_roles
    session = object_session(obj) or obj.__session__

    if session and to_remove:
        to_remove_lr = [
            lr for lr in obj.local_roles
            if lr.principal_id == principal_id and lr.role_name in to_remove
        ]
        for lr in to_remove_lr:
            del_local_role(session, obj, lr)
        session.flush()

    if session and to_add:
        for role_name in to_add:
            add_local_role(session, obj, role_name, principal_id)
        session.flush()


class LocalRolesComparator(BaseComparator):
    """Comparator to filter by role_name and principal_id."""

    def __init__(self, cls: ClassItemType, role_name: str):
        """Initialize local roles comparator."""
        self.cls = cls
        self.role_name = role_name

    def operate(self, op: t.Callable, other: t.Any, escape: t.Optional[str]=None) -> t.Callable:
        """Operate method return the transformation function."""
        def transform(query: Query):
            """Add a join condition with local_roles and add a filter by role_name in the query."""
            cls = self.cls.local_roles.mapper.class_
            query = query.join(cls).filter(
                and_(
                    op(cls.principal_id, other),
                    cls.role_name == self.role_name
                )
            )
            return query
        return transform


def make_lr_attr(actor: str) -> hybrid_property:
    """Create local role hybrid_property attributes."""
    def getter(self):
        """Return the list of user_ids with a local role."""
        return principals_by_role(self, actor)

    def setter(self, values):
        """Update local role collection."""
        set_local_roles_by_role_name(self, actor, values)

    def expression(cls: ClassItemType):
        """Expression that return principal ids from database."""
        return get_lr_expression(cls, actor)

    def comparator(cls: ClassItemType):
        """Return the custom local roles comparator."""
        return LocalRolesComparator(cls, actor)

    lr_attr = hybrid_property(
        fget=getter,
        fset=setter,
        expr=expression,
        custom_comparator=comparator
    )
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
    def _default_can_view(cls) -> set:
        """Generate the default can_view value.

        :returns: set with a list of local role names
        """
        return set(cls.__actors__).union(cls.__additional_can_view_lr__)

    @classmethod
    def query(
            cls,
            principal_id: t.Optional[PrincipalIdType]=None,
            permission: str='can_view'
    ) -> Query:
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
            ).distinct()
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
