"""Briefy LocalRole support for database objects."""
from briefy.common.db.mixins import Identifiable
from briefy.common.db.mixins import Timestamp
from briefy.common.db.model import Base
from briefy.common.vocabularies.roles import LocalRolesChoices

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class LocalRoleDeprecated(Identifiable, Timestamp, Base):
    """Local role support for Briefy."""

    __tablename__ = 'localroles_deprecated'

    entity_type = sa.Column(
        sa.String(255),
        index=True,
        nullable=False
    )
    """Entity type.

    Name of the entity -- as in its classname.
    """

    entity_id = sa.Column(
        sautils.UUIDType(),
        nullable=False,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Entity ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
    )
    """Entity ID.

    ID of the entity that will receive this Local Role.
    """

    user_id = sa.Column(
        sautils.UUIDType(),
        nullable=False,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'User ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
    )
    """User ID.

    User ID assigned the local role here.
    """

    role_name = sa.Column(
        sautils.ChoiceType(LocalRolesChoices, impl=sa.String()),
        nullable=False,
        index=True,
    )
    """Local role name.

    i.e: project_manager
    """

    can_create = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False,
        index=True
    )
    """Boolean indicating a user can create sub-objects."""

    can_delete = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False,
        index=True
    )
    """Boolean indicating a user can delete this object."""

    can_edit = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False,
        index=True
    )
    """Boolean indicating a user can update this object."""

    can_list = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False,
        index=True
    )
    """Boolean indicating a user can list this object."""

    can_view = sa.Column(
        sa.Boolean(),
        nullable=False,
        default=False,
        index=True
    )
    """Boolean indicating a user can read this object."""

    def __repr__(self) -> str:
        """Representation of this object."""
        return (
            """<{0}(id='{1}' entity='{2}' entity_id='{3}' user_id='{4}' role='{5}')>""").format(
                self.__class__.__name__,
                self.id,
                self.entity_type,
                self.entity_id,
                self.user_id,
                self.role_name.value
        )
