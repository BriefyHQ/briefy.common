"""Item base model."""
from briefy.common.db import Base
from briefy.common.db.mixins import LocalRolesMixin
from briefy.common.db.mixins import Mixin
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr

import sqlalchemy as sa
import uuid


class Item(LocalRolesMixin, Mixin, Base):
    """Model class to be used as base for all first level class models."""

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
        if actors_data:
            obj.update(actors_data)

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
