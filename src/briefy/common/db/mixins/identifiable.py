"""Identifiable mixin."""
from briefy.common.utils.data import generate_uuid
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa


class GUID:
    """A Mixin providing a id as primary key.

    The id field is an UUID-4 object.
    """

    id = sa.Column(
        UUIDType(),
        unique=True,
        primary_key=True,
        default=generate_uuid,
        info={
            'colanderalchemy': {
                'title': 'ID',
                'validator': colander.uuid,
                'typ': colander.String
            }
        }
    )
    """ID of the object.

    Primary key using a UUID-4 info.
    """


class GUIDFK:
    """A Mixin providing a id as primary key with FK to base items table.

    The id field is an UUID-4 object.
    """

    @declared_attr
    def id(self):
        """ID of the object and with FK to items tables.

        Primary key using a UUID-4 info.
        """
        return sa.Column(
            UUIDType(),
            sa.ForeignKey('items.id'),
            unique=True,
            primary_key=True,
            default=generate_uuid,
            info={
                'colanderalchemy': {
                    'title': 'ID',
                    'validator': colander.uuid,
                    'typ': colander.String
                }
            }
        )
