"""Identifiable mixin."""
from briefy.common.utils.data import generate_uuid
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa


class GUID:
    """A Mixin providing a id as primary key."""

    id = sa.Column(UUIDType(binary=False), 
                   unique=True,
                   primary_key=True,
                   default=generate_uuid,
                   info={'colanderalchemy': {
                         'title': 'ID',
                         'validator': colander.uuid,
                         'typ': colander.String}
                   })
