"""Item base model."""
from briefy.common.db import Base
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import LocalRolesMixin
from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins import VersionMixin
from briefy.common.db.mixins.local_roles import set_local_roles_by_role_name
from copy import deepcopy
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr

import colander
import sqlalchemy as sa
import uuid


class Item(BaseMetadata, LocalRolesMixin, Mixin, VersionMixin, Base):
    """Model class to be used as base for all first level class models."""

    __tablename__ = 'items'

    path = sa.Column(
        ARRAY(UUID(as_uuid=True)),
        nullable=False,
        index=True,
        info={
            'colanderalchemy': {
                'title': 'Path',
                'missing': colander.drop,
                'typ': colander.List
            }
        }
    )
    """List of all parent objects including itself."""

    type = sa.Column(
        sa.String(50),
        index=True,
        info={
            'colanderalchemy': {
                'title': 'type',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
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

    @classmethod
    def create(cls, payload) -> object:
        """Factory that creates a new instance of this object.

        :param payload: Dictionary containing attributes and values
        :type payload: dict
        """
        # we are going to change the payload so we need to avoid side effects
        payload = deepcopy(payload)
        # add local roles can_view using payload, actors and special attribute from the class
        can_view = payload.get('can_view', [])
        payload['can_view'] = list(set(can_view).union(cls._default_can_view()))
        actors_data = {
            actor: payload.pop(actor) for actor in cls.__actors__ if actor in payload
        }

        obj_id = payload.setdefault('id', uuid.uuid4())
        if isinstance(obj_id, str):
            obj_id = uuid.UUID(obj_id)

        # look for a parent id get the parent instance
        parent_attr = getattr(cls, '__parent_attr__', None)
        parent_id = payload.get(parent_attr, None) if parent_attr else None
        if parent_id:
            parent = Item.get(parent_id)
            path = parent.path
        else:
            path = []
        path.append(obj_id)
        payload['path'] = path

        # create and add to the session the new instance
        obj = cls(**payload)
        session = obj.__session__
        session.add(obj)
        session.flush()

        # add local roles using update method
        if actors_data:
            obj.update(actors_data)

        # TODO: fire object created event here?
        return obj

    def update(self, values):
        """Update the object with given values.

        This implementation take care of update local role attributes.

        :param values: Dictionary containing attributes and values
        :type values: dict
        """
        actors = self.__class__.__actors__
        for key, value in values.items():
            if key not in actors:
                setattr(self, key, value)
            else:
                set_local_roles_by_role_name(self, key, value)

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
