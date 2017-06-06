"""Test Item model and local roles attributes."""
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import SubItemMixin
from briefy.common.db.models import Item
from conftest import DBSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

import pytest
import uuid


customer_data = {
    'customer_manager': [
        '69a624c9-1017-4b47-9c45-ceeea105dc81',
        'ae147521-6fcf-4585-9cb8-361a0339479d'
    ],
    'path': [uuid.UUID('69a624c9-1017-4b47-9c45-ceeea105dc81')],
    'id': '904d5896-c1ff-4380-96f0-53d96748bb1d',
    'title': 'Customer 01',
}

project_data = {
    'customer_pm': ['e9bee447-91ea-468f-b247-1ba4b9cf79ac'],
    'customer_qa': ['3177f78e-6dee-44ce-b939-8135d1a8b777'],
    'project_manager': ['e9bee447-91ea-468f-b247-1ba4b9cf79ac'],
    'qa_manager': ['92a40b92-8c04-407d-9922-097ba5171e2d'],
    'scout_manager': ['edb4d4be-8b22-4818-894e-3da6317087f4'],
    'id': '0bc4a93a-4e9b-4524-ad9a-a75d65018b97',
    'title': 'Project 01',
}

order_data = {
    'project_manager': ['5c78b972-e942-4bf8-a3d8-29b2417f1db2'],
    'qa_manager': ['1b2d1c43-7609-4f73-9eea-d49ef79e215e'],
    'scout_manager': ['64323e01-8662-46d0-a6e6-04d7013fa166'],
    'id': '07ecfbe1-1518-43e6-8632-f36d3874678a',
    'title': 'Order 01',
}

assignment_data = {
    'project_manager': 'e9bee447-91ea-468f-b247-1ba4b9cf79ac',
    'qa_manager': '92a40b92-8c04-407d-9922-097ba5171e2d',
    'scout_manager': 'edb4d4be-8b22-4818-894e-3da6317087f4',
    'id': '872a1092-50ac-4924-b78c-73a20bc4b592',
    'title': 'Assignment 01',
}


class Customer(BaseMetadata, SubItemMixin, Item):
    """Customer model."""

    __tablename__ = 'customers'
    __session__ = DBSession

    @declared_attr
    def _customer_manager(cls):
        """Relationship with customer_manager role_name.

        :return: LocalRoles instances of customer_manager role_name.
        """
        return cls.create_lr_relationship('customer_manager')

    @declared_attr
    def customer_manager(cls) -> list:
        """Return a list of ids of customer_manager.

        :return: IDs of the customer users.
        """
        return cls.create_lr_proxy('customer_manager', DBSession)

    @hybrid_property
    def lr_customer_manager(self) -> list:
        """Return the list of user_ids with local role of customer_manager."""
        return self.customer_manager

    @lr_customer_manager.setter
    def lr_customer_manager(self, values: list):
        """Update customer manager collection"""
        self.set_local_role(values, role_name='customer_manager')


class Project(SubItemMixin, Item):
    """Project model."""

    __tablename__ = 'projects'
    __session__ = DBSession


class Order(SubItemMixin, Item):
    """Order model."""

    __tablename__ = 'orders'
    __session__ = DBSession


class Assignment(SubItemMixin, Item):
    """Assignment model."""

    __tablename__ = 'assignments'
    __session__ = DBSession


model_tuples = (
    ('customer', Customer, customer_data),
    # ('project', Project, project_data),
    # ('order', Order, order_data),
    # ('assignment', Assignment, assignment_data),
)


@pytest.mark.usefixtures('db_transaction')
class TestLocalRoles:
    """Test local roles."""

    @pytest.mark.parametrize('model', model_tuples)
    def test_create_items(self, session, model):
        """Create new model items"""
        attr_name, model, model_data = model
        assert issubclass(model, Item)
        obj = model(**model_data)
        obj_id = obj.id
        session.add(obj)
        session.flush()

        setattr(self, attr_name, obj)
        assert isinstance(obj, Item)

        new_principal = uuid.uuid4()
        obj.attr_customer_manager = [new_principal]
        session.flush()
        session.commit()
        obj = model.get(obj_id)
        assert obj.attr_customer_manager == [new_principal]
