"""Base metadata mixin."""
from briefy.common.utils.data import generate_contextual_slug

import colander
import sqlalchemy as sa


class BaseMetadata:
    """A Mixin providing slug, title and description.

    These fields are used by most, if not all, content objects.
    """

    title = sa.Column('title', sa.String(), nullable=False)
    """Title for the object.

    This is the main display information for the object and it can have UI aliases for each usage

    i.e.: Job Name, Display Name
    """

    description = sa.Column(
        'description',
        sa.Text,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Description',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Description for the object.

    Text field allowing a small, but meaninful description for an object.
    """

    slug = sa.Column('slug',
                     sa.String(255),
                     nullable=True,
                     default=generate_contextual_slug,
                     index=True,
                     info={'colanderalchemy': {
                           'title': 'Description',
                           'missing': colander.drop,
                           'typ': colander.String}}
                     )
    """Slug -- friendly id -- for the object.

    To be used in url.
    """
