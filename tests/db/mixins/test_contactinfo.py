"""Test ContactInfoMixin model."""
from briefy.common.db import Base
from briefy.common.db.mixins import ContactInfoMixin
from briefy.common.db.mixins import Identifiable
from briefy.common.exceptions import ValidationError
from conftest import DBSession

import pytest


@pytest.fixture
def contact_data():
    """Payload for Person object creation."""
    return {
        'id': 'b6771c08-a551-4220-b8cd-09592480b75f',
        'first_name': 'Sebastião',
        'last_name': 'Salgado',
        'company_name': 'Briefy',
        'email': 'sebastiao@email.briefy.co',
        'mobile': '+4917637755474',
        'additional_phone': '+4917637755473',
    }


class Contact(ContactInfoMixin, Identifiable, Base):
    """A Contact."""

    __tablename__ = 'contacts'
    __session__ = DBSession


@pytest.fixture(scope='function')
def contact_instance_obj(session, contact_data):
    """Create an instance of Contact."""
    obj_id = contact_data['id']
    person = Contact(**contact_data)
    session.add(person)
    session.flush()
    obj = Contact.get(obj_id)
    return obj


@pytest.mark.usefixtures('db_transaction')
def test_instance(contact_instance_obj):
    """Create a person instance."""
    assert isinstance(contact_instance_obj, Contact)
    assert contact_instance_obj.display_name == 'Sebastião Salgado'
    assert contact_instance_obj.fullname == 'Sebastião Salgado'


@pytest.mark.usefixtures('db_transaction')
def test_phone_validation_mobile(contact_instance_obj):
    """Test mobile validation."""
    contact = contact_instance_obj
    with pytest.raises(ValidationError) as exc:
        contact.mobile = '004917635467654'

    assert exc.value.message == 'Invalid value for mobile'


@pytest.mark.usefixtures('db_transaction')
def test_phone_validation_additional_phone(contact_instance_obj):
    """Test additional_phone validation."""
    contact = contact_instance_obj
    with pytest.raises(ValidationError) as exc:
        contact.additional_phone = '004917635467654'

    assert exc.value.message == 'Invalid value for additional_phone'
