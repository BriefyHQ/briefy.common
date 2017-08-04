"""Test PersonalInfoMixin model."""
from briefy.common.db import Base
from briefy.common.db.mixins import Identifiable
from briefy.common.db.mixins import PersonalInfoMixin
from conftest import DBSession
from datetime import date
from sqlalchemy.exc import StatementError

import pytest


@pytest.fixture
def personal_data():
    """Payload for Person object creation."""
    return {
        'id': 'b6771c08-a551-4220-b8cd-09592480b75f',
        'first_name': 'Sebastião',
        'last_name': 'Salgado',
        'description': 'A person',
        'gender': 'm',
        'birth_date': date(1980, 3, 22),
    }


class Person(PersonalInfoMixin, Identifiable, Base):
    """A Location."""

    __tablename__ = 'persons'
    __session__ = DBSession


@pytest.fixture(scope='function')
def person_instance_obj(session, personal_data):
    """Create an instance of Person."""
    obj_id = personal_data['id']
    person = Person(**personal_data)
    session.add(person)
    session.flush()
    obj = Person.get(obj_id)
    return obj


@pytest.mark.usefixtures('db_transaction')
def test_instance(person_instance_obj):
    """Create a person instance."""
    assert isinstance(person_instance_obj, Person)
    assert person_instance_obj.display_name == 'Sebastião Salgado'
    assert person_instance_obj.fullname == 'Sebastião Salgado'


@pytest.mark.usefixtures('db_transaction')
def test_age(person_instance_obj):
    """Test age property."""
    assert isinstance(person_instance_obj.age, int)

    person_instance_obj.birth_date = None
    assert person_instance_obj.age is None


@pytest.mark.usefixtures('db_transaction')
def test_gender_validation(session, personal_data):
    """Test gender validation."""
    data = personal_data
    data['gender'] = 'F'
    with pytest.raises(StatementError) as exc:
        person = Person(**personal_data)
        session.add(person)
        session.commit()

    assert 'ValueError' in str(exc)
