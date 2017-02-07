"""Personal information mixin."""
from briefy.common.vocabularies.person import GenderCategories
from datetime import date
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import ChoiceType

import colander
import sqlalchemy as sa
import sqlalchemy_utils as sautils


class NameMixin:
    """A mixin to handle name information."""

    first_name = sa.Column(sa.String(255), index=True, nullable=False, unique=False)
    """First name of a person."""

    last_name = sa.Column(sa.String(255), index=True, nullable=False, unique=False)
    """Last name of a person."""

    @hybrid_property
    def display_name(self) -> str:
        """Display name of this person.

        First try to return the content of title, otherwise, fullname.

        :returns: String providing a display name for this person.
        """
        title = getattr(self, 'title', getattr(self, 'fullname', ''))
        return title

    @declared_attr
    def fullname(cls) -> str:
        """Fullname of this person.

        Concatenates first and last name.

        :returns: Concatenated first and last name of a person.
        """
        return orm.column_property(cls.first_name + ' ' + cls.last_name)


class PersonalInfoMixin(NameMixin):
    """A mixin for personal information."""

    description = sa.Column(
        sa.Text(),
        nullable=True,
        info={
            'colanderalchemy': {
                'title': 'Description',
                'missing': colander.drop,
            }
        }
    )
    """Description (or bio) of a person."""

    gender = sa.Column(
        ChoiceType(GenderCategories, impl=sa.String()),
        nullable=True,
        primary_key=False
    )
    """Gender of a person.

    Options come from :mod:`briefy.common.vocabularies.person`
    """

    birth_date = sa.Column(
        'birth_date',
        sa.Date(),
        nullable=True,
        info={'colanderalchemy': {
              'title': 'Birthdate',
              'missing': colander.drop,
              'typ': colander.Date}}
    )
    """Birth date of a person."""

    @property
    def age(self) -> int:
        """Age of this person, in years.

        :returns: If birth_date is set, calculates the age of the person, in years.
        """
        age = None
        bdate = self.birth_date
        if bdate is not None:
            today = date.today()
            age = (
                today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
            )
        return age


class ContactInfoMixin(NameMixin):
    """A mixin to manage contact information."""

    company_name = sa.Column(
        sa.String(),
        nullable=True,
        unique=False,
        info={
            'colanderalchemy': {
                'title': 'Company',
                'default': '',
                'missing': colander.drop,
                'typ': colander.String
            }
        }
    )
    """Name of the contact person Company."""

    email = sa.Column(
        sautils.types.EmailType(),
        nullable=True,
        unique=False,
        info={
            'colanderalchemy': {
                'title': 'Email',
                'default': '',
                'typ': colander.String
            }
        }
    )
    """Email of the contact person."""

    mobile = sa.Column(
        sautils.types.PhoneNumberType(),
        nullable=True,
        unique=False,
        info={
            'colanderalchemy': {
                'title': 'Mobile phone number',
                'default': '',
                'typ': colander.String
            }
        }
    )
    """Mobile phone number of the contact person."""

    additional_phone = sa.Column(
        sautils.types.PhoneNumberType(),
        nullable=True,
        unique=False,
        info={
            'colanderalchemy': {
                'title': 'Additional Phone',
                'typ': colander.String,
                'missing': colander.drop,
            }
        }
    )
    """Additional phone number of the contact person."""
