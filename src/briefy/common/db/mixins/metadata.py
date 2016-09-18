"""Base metadata mixin."""
from briefy.common.utils.data import generate_slug

import sqlalchemy as sa


class BaseMetadata:
    """A Mixin slug, title and description."""

    title = sa.Column('title', sa.String(), nullable=False)
    description = sa.Column('description', sa.String(), nullable=True)
    _slug = sa.Column('slug', sa.String(255), nullable=True)

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
            slug = '{obj_id}-{title}'.format(
                obj_id=obj_id,
                title=generate_slug(self.title)
            )
        return slug

    @slug.setter
    def slug(self, value: str):
        """Set a new slug for this object.

        :param value: Value of the new slug
        """
        self._slug = value
