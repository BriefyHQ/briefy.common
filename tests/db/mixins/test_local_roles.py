"""Test Item model and local roles attributes."""
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import SubItemMixin
from briefy.common.db.models import Item
from conftest import DBSession
from sqlalchemy.ext.hybrid import hybrid_property

import pytest
import uuid


CUSTOMER_ID_01 = uuid.uuid4()
CUSTOMER_ID_02 = uuid.uuid4()

PROJECT_ID_01 = uuid.uuid4()
PROJECT_ID_02 = uuid.uuid4()

customer_data = [
    {
        'customer_managers': [
            '69a624c9-1017-4b47-9c45-ceeea105dc81',
            'ae147521-6fcf-4585-9cb8-361a0339479d'
        ],
        'id': CUSTOMER_ID_01,
        'title': 'Customer 01',
    },
    {
        'customer_managers': [
            '69a624c9-1017-4b47-9c45-ceeea105dc81',
            'ae147521-6fcf-4585-9cb8-361a0339479d'
        ],
        'id': CUSTOMER_ID_02,
        'title': 'Customer 02',
    },
]

project_data = [
    {
        'parent_id': CUSTOMER_ID_01,
        'customer_pms': ['e9bee447-91ea-468f-b247-1ba4b9cf79ac'],
        # 'customer_qas': ['3177f78e-6dee-44ce-b939-8135d1a8b777'],
        # 'pms': ['e9bee447-91ea-468f-b247-1ba4b9cf79ac'],
        # 'qas': ['92a40b92-8c04-407d-9922-097ba5171e2d'],
        # 'scouts': ['edb4d4be-8b22-4818-894e-3da6317087f4'],
        'id': PROJECT_ID_01,
        'title': 'Project 01',
    },
    {
        'parent_id': CUSTOMER_ID_02,
        'customer_pms': ['e9bee447-91ea-468f-b247-1ba4b9cf79ac'],
        # 'customer_qas': ['3177f78e-6dee-44ce-b939-8135d1a8b777'],
        # 'pms': ['e9bee447-91ea-468f-b247-1ba4b9cf79ac'],
        # 'qas': ['92a40b92-8c04-407d-9922-097ba5171e2d'],
        # 'scouts': ['edb4d4be-8b22-4818-894e-3da6317087f4'],
        'id': PROJECT_ID_02,
        'title': 'Project 02',
    }
]

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

    __actors__ = (
        'customer_managers',
    )

    @hybrid_property
    def customer_managers(self) -> list:
        """Return the list of user_ids with local role of customer_manager."""
        return self.principals_by_role('customer_managers')

    @customer_managers.setter
    def customer_managers(self, values: list):
        """Update customer manager collection"""
        self.set_local_role(values, role_name='customer_managers')

    @customer_managers.expression
    def customer_managers(cls):
        """Expression that return principal ids from database."""
        return cls.get_expression('customer_managers')


class Project(SubItemMixin, BaseMetadata, Item):
    """Project model."""

    __tablename__ = 'projects'
    __session__ = DBSession

    __actors__ = (
        'customer_pms',
        'customer_qas',
        # 'pms',
        # 'qas',
        # 'scouts',
    )

    @hybrid_property
    def customer_pms(self) -> list:
        """Return the list of user_ids with local role of customer_manager."""
        return self.principals_by_role('customer_pms')

    @customer_pms.setter
    def customer_pms(self, values: list):
        """Update customer manager collection"""
        self.set_local_role(values, role_name='customer_pms')

    @customer_pms.expression
    def customer_pms(cls):
        """Expression that return principal ids from database."""
        return cls.get_expression('customer_pms')

    @hybrid_property
    def customer_qas(self) -> list:
        """Return the list of user_ids with local role of customer_manager."""
        return self.principals_by_role('customer_qas')

    @customer_qas.setter
    def customer_qas(self, values: list):
        """Update customer manager collection"""
        self.set_local_role(values, role_name='customer_qas')

    @customer_qas.expression
    def customer_qas(cls):
        """Expression that return principal ids from database."""
        return cls.get_expression('customer_qas')


class Order(SubItemMixin, Item):
    """Order model."""

    __tablename__ = 'orders'
    __session__ = DBSession


class Assignment(SubItemMixin, Item):
    """Assignment model."""

    __tablename__ = 'assignments'
    __session__ = DBSession


model_tuples = (
    ('customer', Customer, customer_data, ('customer_managers', )),
    ('project', Project, project_data, ('customer_pms', 'customer_qas', )),
    # ('order', Order, order_data),
    # ('assignment', Assignment, assignment_data),
)


@pytest.mark.usefixtures('db_transaction')
class TestLocalRoles:
    """Test local roles."""

    @pytest.mark.parametrize('model', model_tuples)
    def test_create_items(self, session, model):
        """Create new model items"""
        attr_name, model, model_data, roles = model
        assert issubclass(model, Item)

        for payload in model_data:
            obj = model.create(payload)
            obj_id = obj.id
            session.add(obj)
            session.flush()

            assert isinstance(obj, Item)

            for role_name in roles:
                new_principal = uuid.uuid4()
                setattr(obj, role_name, [new_principal])

                obj = model.get(obj_id)
                role_attr_value = getattr(obj, role_name)
                assert role_attr_value == [new_principal]

                role_attr = getattr(model, role_name)

                items = session.query(model).filter(
                    role_attr.in_([new_principal])
                ).all()

                assert obj.id == items[0].id
