"""Roles mixins."""
from briefy.common.types import BaseUser
from briefy.common.vocabularies.roles import LocalRolesChoices
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import relationship
from uuid import UUID

import sqlalchemy as sa


class LocalRolesMixin:
    """A mixin providing Local role support for an object."""

    __actors__ = ()

    @classmethod
    def get_permission_relationship(cls, permission_name, viewonly=True, uselist=True):
        """Get Local Role permission relationship."""
        return sa.orm.relationship(
            'LocalRole',
            foreign_keys='LocalRole.item_id',
            viewonly=viewonly,
            uselist=uselist,
            primaryjoin="""and_(
                        LocalRole.item_id=={entity}.id,
                        LocalRole.{permission_name}==True,
                    )""".format(
                entity=cls.__name__,
                permission_name=permission_name
            )
        )

    @classmethod
    def permission_association_proxy(cls, local_attr, remote_attr='user_id'):
        """Get a new permission association proxy instance."""
        return association_proxy(local_attr, remote_attr)

    @declared_attr
    def can_view_roles(cls):
        """Relationship: return a list of LocalRoles that have the permission can_view.

        :return: list of LocalRoles model instances.
        """
        return cls.get_permission_relationship('can_view')

    @declared_attr
    def can_view_users(cls):
        """Return a list of user IDs that have the can_view permission.

        :return: list of user IDs
        """
        return cls.permission_association_proxy('can_view_roles')

    @declared_attr
    def can_edit_roles(cls):
        """Relationship: return a list of LocalRoles that have the permission can_edit.

        :return: list of LocalRoles model instances.
        """
        return cls.get_permission_relationship('can_edit')

    @declared_attr
    def can_edit_users(cls):
        """Return a list of user IDs that have the can_edit permission.

        :return: list of user IDs
        """
        return cls.permission_association_proxy('can_edit_roles')

    @declared_attr
    def can_delete_roles(cls):
        """Relationship: return a list of LocalRoles that have the permission can_delete.

        :return: list of LocalRoles model instances.
        """
        return cls.get_permission_relationship('can_delete')

    @declared_attr
    def can_delete_users(cls):
        """Return a list of user IDs that have the can_delete permission.

        :return: list of user IDs
        """
        return cls.permission_association_proxy('can_delete_roles')

    @declared_attr
    def can_create_roles(cls):
        """Relationship: return a list of LocalRoles that have the permission can_create.

        :return: list of LocalRoles model instances.
        """
        return cls.get_permission_relationship('can_create')

    @declared_attr
    def can_create_users(cls):
        """Return a list of user IDs that have the can_create permission.

        :return: list of user IDs
        """
        return cls.permission_association_proxy('can_create_roles')

    @declared_attr
    def can_list_roles(cls):
        """Relationship: return a list of LocalRoles that have the permission can_list.

        :return: list of LocalRoles model instances.
        """
        return cls.get_permission_relationship('can_list')

    @declared_attr
    def can_list_users(cls):
        """Return a list of user IDs that have the can_list permission.

        :return: list of user IDs
        """
        return cls.permission_association_proxy('can_list_roles')

    @declared_attr
    def local_roles(cls):
        """Relationship with LocalRoles."""
        return relationship(
            'LocalRole',
            foreign_keys='LocalRole.entity_id',
            primaryjoin="""and_(
                LocalRole.entity_id=={entity}.id,
                LocalRole.entity_type=="{entity}",
            )""".format(
                entity=cls.__name__
            ),
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
        from briefy.common.db.models.roles import LocalRoleDeprecated

        return sa.select(
            [LocalRoleDeprecated.user_id]
        ).where(
            sa.and_(
                cls.__name__ == LocalRoleDeprecated.entity_type,
                cls.id == LocalRoleDeprecated.entity_id,
            )
        ).as_scalar()

    def _actors_info(self) -> dict:
        """Return actor information for this object.

        :return: Dictionary with attr name and user id.
        """
        actors = {attr: [] for attr in self.__actors__}
        for actor in actors:
            value = getattr(self, actor, None)
            if value and isinstance(value, (UUID, str)):
                actors[actor].append(str(value))
            elif value:
                for item in value:
                    if isinstance(item, (UUID, str)):
                        actors[actor].append(str(item))
                    else:
                        actors[actor].append(str(item.user_id))
        return actors

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

    def add_local_role(self, user: BaseUser, role_name: str, permissions: list = ()) -> None:
        """Add a local role on this object to a user with given user_id.

        :param user: User id.
        :param role_name: Name of the role.
        :param permissions: list of allowed permissions
        """
        from briefy.common.db.models.roles import LocalRole

        # make sure we add a new vocabulary instance and not a simple string
        if not isinstance(role_name, LocalRolesChoices):
            role_name = getattr(LocalRolesChoices, role_name)

        if not self.get_local_role_for_user(role_name, user):
            payload = {
                'entity_type': self.__class__.__name__,
                'entity_id': self.id,
                'user_id': user.id,
                'role_name': role_name,
            }
            # enable permissions: view, edit, create, delete, list
            for perm in permissions:
                perm_name = 'can_{perm}'.format(perm=perm)
                payload[perm_name] = True

            local_role = LocalRole(**payload)
            self.local_roles.append(local_role)
        else:
            raise ValueError(
                'User {user_id} already has {role} local role'.format(
                    user_id=user.id, role=role_name.value
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

    def _add_local_role_user_id(self, user_id: str, role_name: str, permissions: list) -> None:
        """Add a new local role for a user with the given id.

        :param user_id: ID of the user that will receive the local role.
        :param role_name: Local role name
        """
        if user_id:
            user = BaseUser(user_id, {})
            self.add_local_role(user, role_name, permissions)

    def _filter_lr_by_name(self, local_roles: list, role_name: str) -> list:
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
        self._add_local_role_user_id(user_id, 'project_manager', ['view', 'list'])

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
        self._add_local_role_user_id(user_id, 'qa_manager', ['view', 'list'])

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
        self._add_local_role_user_id(user_id, 'scout_manager', ['view', 'list'])
