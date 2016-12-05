"""Base metadata mixin."""
from briefy.common.utils.data import generate_slug

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


    _slug = sa.Column('slug',
                      sa.String(255),
                      nullable=True,
                      info={'colanderalchemy': {
                          'title': 'Description',
                          'missing': colander.drop,
                          'typ': colander.String}}
                      )
    """Slug -- friendly id -- for the object.

    To be used in url.
    """

    @property
    def slug(self) -> str:
        """Return a slug for an object.

        If slug has not been set on this object, fallback to a composition of
        the first 8 chars of an id field, and a slug of the title itself.

        :return: A slug to be added to an url.
        """
        slug = self._slug
        if not slug:
            obj_id = getattr(self, 'id', None)
            if obj_id:
                # Return just the first 8 chars of an uuid
                obj_id = str(obj_id)[:8]
            else:
                obj_id = ''
            title = str(self.title)
            slug = '{obj_id}-{title}'.format(
                obj_id=obj_id,
                title=generate_slug(title)
            )
        return slug

    @slug.setter
    def slug(self, value: str):
        """Set a new slug for this object.

        :param value: Value of the new slug
        """
        self._slug = value
