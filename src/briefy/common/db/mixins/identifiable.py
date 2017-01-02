"""Identifiable mixin."""
from briefy.common.utils.data import generate_uuid
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
