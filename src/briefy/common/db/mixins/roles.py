"""Roles mixins."""
from briefy.common.types import BaseUser
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_method

import sqlalchemy as sa


class LocalRolesMixin:
    """A mixin providing Local role support for an object."""

    __actors__ = ()

    @declared_attr
    def local_roles(cls):
        """Relationship with LocalRoles."""
        return relationship(
            'LocalRole',
            foreign_keys='LocalRole.entity_id',
            primaryjoin='''and_(
                LocalRole.entity_id=={entity}.id,
                LocalRole.entity_type=="{entity}",
            )'''.format(
                entity=cls.__name__
            ),
            lazy='joined'
        )

    @hybrid_method
    def get_user_roles(self, user: BaseUser) -> list:
        """List of Local Roles for a User.

        :param user: User object
        """
        user_id = user.id
        roles = self.local_roles
        return [lr for lr in roles if str(lr.user_id) == user_id]

    @get_user_roles.expression
    def get_user_roles(cls, user: BaseUser) -> list:
        """List of Local Roles for a User.

        :param user: User object
        """
        from briefy.common.db.models.roles import LocalRole

        user_id = user.id
        return LocalRole.query().filter(
            sa.and_(
                cls.__name__ == LocalRole.entity_type,
                cls.id == LocalRole.entity_id,
                user_id == LocalRole.user_id,
            )
        )

    def get_local_role_for_user(self, role_name: str, user: BaseUser) -> object:
        """Return a Local for an user_id.

        :param user: User object
        :param role_name: Name of the role.
        """
        roles = [lr for lr in self.get_user_roles(user) if lr.role_name.value == role_name]
        return roles[0] if roles else None

    @hybrid_method
    def _actors_ids(self) -> list:
        """List of actors ids for this object.

        :return: List of actor ids.
        """
        return [str(lr.user_id) for lr in self.local_roles]

    @_actors_ids.expression
    def _actors_ids(cls) -> list:
        """List of actors ids for this object.

        :return: List of actor ids.
        """
        from briefy.common.db.models.roles import LocalRole

        return sa.select(
            [LocalRole.user_id]
        ).where(
            sa.and_(
                cls.__name__ == LocalRole.entity_type,
                cls.id == LocalRole.entity_id,
            )
        ).as_scalar()

    def _actors_info(self) -> dict:
        """Return actor information for this object.

        :return: Dictionary with attr name and user id.
        """
        actors = {attr: [] for attr in self.__actors__}
        for lr in self.local_roles:
            actors[lr.role_name.value].append(str(lr.user_id))
        return actors

    @hybrid_method
    def _can_list(self, user: BaseUser) -> bool:
        """Check if the user can list this object.

        :param user: User object..
        :return: Boolean indicating if user is allowed to list this object.
        """
        user_groups = set(getattr(user, 'groups'))
        acl = dict(getattr(self, '__raw_acl__'))
        allowed = set(acl.get('list', []))
        if user_groups.intersection(allowed):
            return True
        else:
            roles = self.get_user_roles(user)
            can_list = [lr for lr in roles if lr.can_view]
            return True if can_list else False

    @hybrid_method
    def is_actor(self, user_id: str) -> bool:
        """Check if the user_id is an actor in this object.

        :param user_id: UUID of an user.
        :return: Check if this id is for a user in here.
        """
        return user_id in [u for u in self._actors_ids()]

    @is_actor.expression
    def is_actor(cls, user_id: str) -> bool:
        """Check if the user_id is an actor in this object.

        :param user_id: UUID of an user.
        :return: Check if this id is for a user in here.
        """
        return user_id in [u for u in cls._actors_ids()]

    def add_local_role(self, user: BaseUser, role_name: str) -> None:
        """Add a local role on this object to a user with given user_id.

        :param user: User id.
        :param role_name: Name of the role.
        """
        from briefy.common.db.models.roles import LocalRole

        if not self.get_local_role_for_user(role_name, user):
            payload = {
                'entity_type': self.__class__.__name__,
                'entity_id': self.__class__.__name__,
                'user_id': user.id,
                'role_name': role_name,
            }
            local_role = LocalRole(**payload)
            self.local_roles.append(local_role)
        else:
            raise ValueError(
                'User {user_id} already has {role} local role'.format(
                    user_id=user.id, role=role_name
                )
            )

    def remove_local_role(self, user: BaseUser, role_name: str) -> None:
        """Remove a local role on this object to a user with given user_id.

        :param user_id: User id.
        :param role_name: Name of the role.
        """
        role = self.get_local_role_for_user(role_name, user)

        if role:
            session = getattr(self, '__session__')
            session.delete(role)
        else:
            raise ValueError(
                'User {user_id} does not have {role} local role'.format(
                    user_id=user.id, role=role_name
                )
            )


class BaseBriefyRoles(LocalRolesMixin):
    """A Base Mixin providing internal Briefy roles for an object."""

    __actors__ = ()

    def _add_local_role_user_id(self, user_id: str, role_name: str) -> None:
        """Add a new local role for a user with the given id.

        :param user_id: ID of the user that will receive the local role.
        :param role_name: Local role name
        """
        if user_id:
            user = BaseUser(user_id, {})
            self.add_local_role(user, role_name)

    @staticmethod
    def _filter_lr_by_name(local_roles: list, role_name: str) -> list:
        """Filter LocalRole by role names.

        :param local_roles: List of Local Roles
        :param role_name: Role name, i.e: project_manager
        """
        return [lr for lr in local_roles if lr.role_name.value == role_name]


class BriefyRoles(BaseBriefyRoles):
    """A Mixin providing internal Briefy roles for an object."""

    __actors__ = (
        'project_manager',
        'scout_manager',
        'qa_manager',
    )

    @property
    def project_manager(self) -> list:
        """Return a list of ids of project managers.

        :return: ID of the project_manager.
        """
        roles = self.local_roles
        return self._filter_lr_by_name(roles, 'project_manager')

    @project_manager.setter
    def project_manager(self, user_id: str) -> None:
        """Set a new project_manager for this object.

        :param user_id: ID of the project_manager.
        """
        self._add_local_role_user_id(user_id, 'project_manager')

    @property
    def qa_manager(self) -> list:
        """Return a list of ids of qa_managers.

        :return: ID of the qa_manager.
        """
        roles = self.local_roles
        return self._filter_lr_by_name(roles, 'qa_manager')

    @qa_manager.setter
    def qa_manager(self, user_id: str) -> None:
        """Set a new qa_manager for this object.

        :param user_id: ID of the qa_manager.
        """
        self._add_local_role_user_id(user_id, 'qa_manager')

    @property
    def scout_manager(self) -> list:
        """Return a list of ids of scout_managers.

        :return: ID of the scout_manager.
        """
        roles = self.local_roles
        return self._filter_lr_by_name(roles, 'scout_manager')

    @scout_manager.setter
    def scout_manager(self, user_id: str) -> None:
        """Set a new scout_manager for this object.

        :param user_id: ID of the scout_manager.
        """
        self._add_local_role_user_id(user_id, 'scout_manager')
