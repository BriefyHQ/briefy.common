"""Test Item model and local roles attributes."""
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import SubItemMixin
from briefy.common.db.models import Item
from conftest import DBSession

import pytest
import uuid


CUSTOMER_ID_01 = uuid.uuid4()
CUSTOMER_ID_02 = uuid.uuid4()

PROJECT_ID_01 = uuid.uuid4()
PROJECT_ID_02 = uuid.uuid4()

ORDER_ID_01 = uuid.uuid4()
ORDER_ID_02 = uuid.uuid4()

ASSIGNMENT_ID_01 = uuid.uuid4()
ASSIGNMENT_ID_02 = uuid.uuid4()

CUSTOMER_MANAGERS_01 = uuid.uuid4()
CUSTOMER_MANAGERS_02 = uuid.uuid4()

CUSTOMER_PMS_01 = uuid.uuid4()
CUSTOMER_PMS_02 = uuid.uuid4()

CUSTOMER_QAS_01 = uuid.uuid4()
CUSTOMER_QAS_02 = uuid.uuid4()

CUSTOMER_QA_01 = uuid.uuid4()
CUSTOMER_QA_02 = uuid.uuid4()

PMS_01 = uuid.uuid4()
PMS_02 = uuid.uuid4()

QAS_01 = uuid.uuid4()
QAS_02 = uuid.uuid4()

SCOUTS_01 = uuid.uuid4()
SCOUTS_02 = uuid.uuid4()

PROFESSIONAL_USER_01 = uuid.uuid4()
PROFESSIONAL_USER_02 = uuid.uuid4()

QA_MANAGER_01 = uuid.uuid4()
QA_MANAGER_02 = uuid.uuid4()

SCOUT_MANAGER_01 = uuid.uuid4()
SCOUT_MANAGER_02 = uuid.uuid4()


customer_data = [
    {
        'customer_managers': [CUSTOMER_MANAGERS_01],
        'id': CUSTOMER_ID_01,
        'title': 'Customer 01',
        'can_view': ['customer_managers', ]
    },
    {
        'customer_managers': [CUSTOMER_MANAGERS_02],
        'id': CUSTOMER_ID_02,
        'title': 'Customer 02',
        'can_view': ['customer_managers', ]
    },
]

project_data = [
    {
        'parent_id': CUSTOMER_ID_01,
        'customer_pms': [CUSTOMER_PMS_01],
        'customer_qas': [CUSTOMER_QAS_01],
        'pms': [PMS_01],
        'qas': [QAS_01],
        'scouts': [SCOUTS_01],
        'id': PROJECT_ID_01,
        'title': 'Project 01',
        'can_view': [
            'customer_managers', 'customer_pms', 'customer_qas', 'pms', 'qas', 'scouts',
        ]
    },
    {
        'parent_id': CUSTOMER_ID_02,
        'customer_pms': [CUSTOMER_PMS_02],
        'customer_qas': [CUSTOMER_QAS_02],
        'pms': [PMS_02],
        'qas': [QAS_02],
        'scouts': [SCOUTS_02],
        'id': PROJECT_ID_02,
        'title': 'Project 02',
        'can_view': [
            'customer_managers', 'customer_pms', 'customer_qas', 'pms', 'qas', 'scouts',
        ]
    }
]

order_data = [
    {
        'parent_id': PROJECT_ID_01,
        'customer_qa': [CUSTOMER_QA_01],
        'id': ORDER_ID_01,
        'title': 'Order 01',
        'can_view': [
            'customer_managers', 'customer_pms', 'customer_qas', 'customer_qa',
            'pms', 'qas', 'scouts',
        ]
    },
    {
        'parent_id': PROJECT_ID_02,
        'customer_qa': [CUSTOMER_QA_02],
        'id': ORDER_ID_02,
        'title': 'Order 02',
        'can_view': [
            'customer_managers', 'customer_pms', 'customer_qas', 'customer_qa',
            'pms', 'qas', 'scouts',
        ]
    }

]

assignment_data = [
    {
        'parent_id': ORDER_ID_01,
        'professional_user': [PROFESSIONAL_USER_01],
        'qa_manager': [QA_MANAGER_01],
        'scout_manager': [SCOUT_MANAGER_01],
        'id': ASSIGNMENT_ID_01,
        'title': 'Assignment 01',
        'can_view': [
            'qa_manager', 'scout_manager', 'professional_user',
        ]
    },
    {
        'parent_id': ORDER_ID_02,
        'professional_user': [PROFESSIONAL_USER_02],
        'qa_manager': [QA_MANAGER_02],
        'scout_manager': [SCOUT_MANAGER_02],
        'id': ASSIGNMENT_ID_02,
        'title': 'Assignment 02',
        'can_view': [
            'qa_manager', 'scout_manager', 'professional_user',
        ]
    },

]


asset_data = [
    {
        'parent_id': ASSIGNMENT_ID_01,
        'id': uuid.uuid4(),
        'title': 'Asset 01',
        'can_view': [
            'qa_manager', 'scout_manager', 'professional_user',
            'pms', 'qas', 'scouts', 'customer_qa',
            'customer_managers', 'customer_qas', 'customer_pms'
        ]
    },
    {
        'parent_id': ASSIGNMENT_ID_02,
        'id': uuid.uuid4(),
        'title': 'Asset 02',
        'can_view': [
            'qa_manager', 'scout_manager', 'professional_user',
            'pms', 'qas', 'scouts', 'customer_qa',
            'customer_managers', 'customer_qas', 'customer_pms'
        ]
    },

]


class Customer(SubItemMixin, BaseMetadata, Item):
    """Customer model."""

    __tablename__ = 'customers'
    __session__ = DBSession

    __actors__ = (
        'customer_managers',
    )


class Project(SubItemMixin, BaseMetadata, Item):
    """Project model."""

    __tablename__ = 'projects'
    __session__ = DBSession

    __actors__ = (
        'customer_pms',
        'customer_qas',
        'pms',
        'qas',
        'scouts',
    )


class Order(SubItemMixin, BaseMetadata, Item):
    """Order model."""

    __tablename__ = 'orders'
    __session__ = DBSession

    __actors__ = (
        'customer_qa',
    )


class Assignment(SubItemMixin, BaseMetadata, Item):
    """Assignment model."""

    __tablename__ = 'assignments'
    __session__ = DBSession

    __actors__ = (
        'qa_manager',
        'scout_manager',
        'professional_user'
    )


class Asset(SubItemMixin, BaseMetadata, Item):
    """Asset model."""

    __tablename__ = 'assets'
    __session__ = DBSession


MODELS = {
    'customer': {
        'model': Customer,
        'data': customer_data,
        'local_roles': Customer.__actors__,
        'can_view': 'can_view'
    },
    'project': {
        'model': Project,
        'data': project_data,
        'local_roles': Project.__actors__,
        'can_view': 'can_view'
    },
    'order': {
        'model': Order,
        'data': order_data,
        'local_roles': Order.__actors__,
        'can_view': 'can_view'
    },
    'assignment': {
        'model': Assignment,
        'data': assignment_data,
        'local_roles': Assignment.__actors__,
        'can_view': 'can_view'
    },
    'asset': {
        'model': Asset,
        'data': asset_data,
        'local_roles': Asset.__actors__,
        'can_view': 'can_view'
    },
}


PERMISSIONS = {
    'customer_managers': {
        'customer': (Customer, customer_data, True, False),
        'project': (Project, project_data, True, False),
        'order': (Order, order_data, True, False),
        'assignment': (Assignment, assignment_data, False, False),
        'asset': (Asset, asset_data, True, False)
    },
    'customer_qas': {
        'customer': (Customer, customer_data, False, False),
        'project': (Project, project_data, True, False),
        'order': (Order, order_data, True, False),
        'assignment': (Assignment, assignment_data, False, False),
        'asset': (Asset, asset_data, True, False)
    },
    'customer_pms': {
        'customer': (Customer, customer_data, False, False),
        'project': (Project, project_data, True, False),
        'order': (Order, order_data, True, False),
        'assignment': (Assignment, assignment_data, False, False),
        'asset': (Asset, asset_data, True, False)
    },
    'qas': {
        'customer': (Customer, customer_data, False, False),
        'project': (Project, project_data, True, False),
        'order': (Order, order_data, True, False),
        'assignment': (Assignment, assignment_data, False, False),
        'asset': (Asset, asset_data, True, False)
    },
    'pms': {
        'customer': (Customer, customer_data, False, False),
        'project': (Project, project_data, True, False),
        'order': (Order, order_data, True, False),
        'assignment': (Assignment, assignment_data, False, False),
        'asset': (Asset, asset_data, True, False)
    },
    'scouts': {
        'customer': (Customer, customer_data, False, False),
        'project': (Project, project_data, True, False),
        'order': (Order, order_data, True, False),
        'assignment': (Assignment, assignment_data, False, False),
        'asset': (Asset, asset_data, True, False)
    },
    'customer_qa': {
        'customer': (Customer, customer_data, False, False),
        'project': (Project, project_data, False, False),
        'order': (Order, order_data, True, False),
        'assignment': (Assignment, assignment_data, False, False),
        'asset': (Asset, asset_data, True, False)
    },
    'qa_manager': {
        'customer': (Customer, customer_data, False, False),
        'project': (Project, project_data, False, False),
        'order': (Order, order_data, False, False),
        'assignment': (Assignment, assignment_data, True, False),
        'asset': (Asset, asset_data, True, False)
    },
    'scout_manager': {
        'customer': (Customer, customer_data, False, False),
        'project': (Project, project_data, False, False),
        'order': (Order, order_data, False, False),
        'assignment': (Assignment, assignment_data, True, False),
        'asset': (Asset, asset_data, True, False)
    },
    'professional_user': {
        'customer': (Customer, customer_data, False, False),
        'project': (Project, project_data, False, False),
        'order': (Order, order_data, False, False),
        'assignment': (Assignment, assignment_data, True, False),
        'asset': (Asset, asset_data, True, False)
    },
}


@pytest.mark.usefixtures('db_transaction')
class TestLocalRoles:
    """Test local roles."""

    @pytest.mark.parametrize('model_name', tuple(MODELS))
    def test_create_items(self, session, model_name):
        """Create new model items."""
        data = MODELS[model_name]
        model = data['model']
        model_data = data['data']
        roles = data['local_roles']
        assert issubclass(model, Item)

        for payload in model_data:
            obj = model.create(payload)
            obj_id = obj.id

            assert isinstance(obj, Item)

            for role_name in roles:
                old_roles = getattr(obj, role_name)
                new_principal = uuid.uuid4()
                setattr(obj, role_name, [new_principal])
                session.flush()

                obj = model.get(obj_id)
                role_attr_value = getattr(obj, role_name)
                assert role_attr_value == [new_principal]

                role_attr = getattr(model, role_name)
                items = session.query(model).filter(
                    role_attr.in_([new_principal])
                ).all()
                assert obj.id == items[0].id

                setattr(obj, role_name, old_roles)
                role_attr_value = getattr(obj, role_name)
                assert role_attr_value == old_roles

    @pytest.mark.parametrize('model_name', tuple(MODELS))
    def test_query_items_no_inheritance(self, model_name):
        """Query model items."""
        data = MODELS[model_name]
        model = data['model']
        model_data = data['data']
        roles = data['local_roles']

        for payload in model_data:
            obj = model.get(payload['id'])
            for role_name in roles:
                principal_id = getattr(obj, role_name)[0]
                items = model.query(principal_id=principal_id)
                assert obj in items.all()

    @staticmethod
    def validate_permissions(model_name, role_name, base_data):
        """Validate if user can view only their data."""
        data = MODELS[model_name]
        model = data['model']
        model_data = data['data']
        obj_01 = model.get(model_data[0]['id'])
        obj_02 = model.get(model_data[1]['id'])

        condition01 = PERMISSIONS[role_name][model_name][2]
        condition02 = PERMISSIONS[role_name][model_name][3]

        items = model.query(principal_id=base_data[0][role_name][0])
        assert (obj_01 in items.all()) == condition01
        assert (obj_02 in items.all()) == condition02

        items = model.query(principal_id=base_data[1][role_name][0])
        assert (obj_02 in items.all()) == condition01
        assert (obj_01 in items.all()) == condition02

    @pytest.mark.parametrize(
        'model_name', ['customer', 'project', 'order', 'assignment', 'asset']
    )
    def test_customer_managers_can_only_view_their_data(self, model_name):
        """Make sure customer managers can only view their data."""
        role_name = 'customer_managers'
        base_data = MODELS['customer']['data']
        self.validate_permissions(model_name, role_name, base_data)

    @pytest.mark.parametrize(
        'model_name', ['customer', 'project', 'order', 'assignment', 'asset']
    )
    def test_customer_qas_can_only_view_their_data(self, model_name):
        """Make sure customer qas can only view their project, orders and assets."""
        role_name = 'customer_qas'
        base_data = MODELS['project']['data']
        self.validate_permissions(model_name, role_name, base_data)

    @pytest.mark.parametrize(
        'model_name', ['customer', 'project', 'order', 'assignment', 'asset']
    )
    def test_customer_pms_can_only_view_their_data(self, model_name):
        """Make sure customer pms can only view their project, orders and assets."""
        role_name = 'customer_pms'
        base_data = MODELS['project']['data']
        self.validate_permissions(model_name, role_name, base_data)

    @pytest.mark.parametrize(
        'model_name', ['customer', 'project', 'order', 'assignment', 'asset']
    )
    def test_pms_can_only_view_their_data(self, model_name):
        """Make sure pms can only view their project, orders and assets."""
        role_name = 'pms'
        base_data = MODELS['project']['data']
        self.validate_permissions(model_name, role_name, base_data)

    @pytest.mark.parametrize(
        'model_name', ['customer', 'project', 'order', 'assignment', 'asset']
    )
    def test_qas_can_only_view_their_data(self, model_name):
        """Make sure qas can only view their project, orders and assets."""
        role_name = 'qas'
        base_data = MODELS['project']['data']
        self.validate_permissions(model_name, role_name, base_data)

    @pytest.mark.parametrize(
        'model_name', ['customer', 'project', 'order', 'assignment', 'asset']
    )
    def test_scouts_can_only_view_their_data(self, model_name):
        """Make sure scouts can only view their project, orders and assets."""
        role_name = 'scouts'
        base_data = MODELS['project']['data']
        self.validate_permissions(model_name, role_name, base_data)

    @pytest.mark.parametrize(
        'model_name', ['customer', 'project', 'order', 'assignment', 'asset']
    )
    def test_customer_qa_can_only_view_their_data(self, model_name):
        """Make sure customer qa can only view their project, orders and assets."""
        role_name = 'customer_qa'
        base_data = MODELS['order']['data']
        self.validate_permissions(model_name, role_name, base_data)

    @pytest.mark.parametrize(
        'model_name', ['customer', 'project', 'order', 'assignment', 'asset']
    )
    def test_qa_manager_can_only_view_their_data(self, model_name):
        """Make sure qa manager can only view their project, orders and assets."""
        role_name = 'qa_manager'
        base_data = MODELS['assignment']['data']
        self.validate_permissions(model_name, role_name, base_data)

    @pytest.mark.parametrize(
        'model_name', ['customer', 'project', 'order', 'assignment', 'asset']
    )
    def test_scout_manager_can_only_view_their_data(self, model_name):
        """Make sure scout manager can only view their project, orders and assets."""
        role_name = 'scout_manager'
        base_data = MODELS['assignment']['data']
        self.validate_permissions(model_name, role_name, base_data)

    @pytest.mark.parametrize(
        'model_name', ['customer', 'project', 'order', 'assignment', 'asset']
    )
    def test_professional_user_can_only_view_their_data(self, model_name):
        """Make sure professional_user can only view their project, orders and assets."""
        role_name = 'professional_user'
        base_data = MODELS['assignment']['data']
        self.validate_permissions(model_name, role_name, base_data)
