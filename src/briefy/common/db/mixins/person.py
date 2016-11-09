"""Personal information mixin."""
from briefy.common.vocabularies.person import GenderCategories
from datetime import date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import ChoiceType

import sqlalchemy as sa


class NameMixin:
    """A mixin to handle name information."""

    first_name = sa.Column(sa.String(255), nullable=False, unique=False)
    last_name = sa.Column(sa.String(255), nullable=False, unique=False)
    display_name = sa.Column(sa.String(255), nullable=True, unique=False)

    @hybrid_property
    def fullname(self):
        """Fullname of this person."""
        return '{first_name} {last_name}'.format(
            first_name=self.first_name,
            last_name=self.last_name,
        )


class PersonalInfoMixin(NameMixin):
    """A mixin for personal information."""

    description = sa.Column(sa.Text(), nullable=True)
    gender = sa.Column(
        ChoiceType(GenderCategories, impl=sa.String()),
        nullable=True,
        primary_key=False
    )
    birth_date = sa.Column('birth_date', sa.Date(), nullable=True)

    @hybrid_property
    def age(self):
        """Age of this person."""
        age = None
        bdate = self.birth_date
        if bdate:
            today = date.today()
            age = (
                today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
            )
        return age
