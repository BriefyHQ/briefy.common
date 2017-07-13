"""Item base model."""
from briefy.common.db import Base
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import LocalRolesMixin
from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins import VersionMixin
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

        # add local roles
        if actors_data:
            for actor_name, actor_value in actors_data.items():
                actor_attr = getattr(obj, actor_name)
                actor_attr.extend(actor_value)
            # obj.update(actors_data)

        session.flush()

        # TODO: fire object created event here?
        return obj

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
