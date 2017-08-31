"""Base metadata mixin."""
from briefy.common.utils.data import generate_contextual_slug
from sqlalchemy.ext.hybrid import hybrid_property

import colander
import sqlalchemy as sa


class BaseMetadata:
    """A Mixin providing slug, title and description.

    These fields are used by most, if not all, content objects.
    """

    _title = sa.Column(
        'title',
        sa.String(),
        index=True,
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Title',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Title for the object.

    This is the main display information for the object and it can have UI aliases for each usage

    i.e.: Job Name, Display Name
    """

    _description = sa.Column(
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

    Text field allowing a small, but meaningful description for an object.
    """

    _slug = sa.Column('slug',
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

    @hybrid_property
    def title(self) -> str:
        """Title for the object.

        This is the main display information for the object and it can have
        UI aliases for each usage i.e.: Job Name, Display Name

        :return: The title string.
        """
        return self._title

    @title.setter
    def title(self, value: str):
        """Set a new title for this object.

        :param value: Value of the new title
        """
        self._title = value

    @hybrid_property
    def description(self) -> str:
        """Description for the object.

        Text field allowing a small, but meaningful description for an object.

        :return: The description string.
        """
        return self._description

    @description.setter
    def description(self, value: str):
        """Set a new description for this object.

        :param value: Value of the new description
        """
        self._description = value

    @hybrid_property
    def slug(self) -> str:
        """Return a slug for an object.

        :return: A slug to be added to an url.
        """
        return self._slug

    @slug.setter
    def slug(self, value: str):
        """Set a new slug for this object.

        If the value is None, we generate a new one using
        :func:`briefy.common.utils.data.generate_contextual_slug`
        :param value: Value of the new slug
        """
        if not value:
            data = dict(id=self.id, title=self.title)
            value = generate_contextual_slug(data)
        self._slug = value

    def to_dict(self, excludes: list=None, includes: list=None) -> dict:
        """Return a dictionary with fields and values used by this Class.

        :param excludes: attributes to exclude from dict representation.
        :param includes: attributes to include from dict representation.
        :returns: Dictionary with fields and values used by this Class
        """
        add_fields = ('title', 'description', 'slug', )
        data = super().to_dict(excludes, includes)
        excludes = excludes if excludes else []
        for field in add_fields:
            if field not in excludes and field not in data:
                data[field] = getattr(self, field)
        return data
