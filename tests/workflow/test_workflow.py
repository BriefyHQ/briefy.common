"""Tests for `briefy.common.workflow` package."""
from base_workflow import Customer
from base_workflow import CustomerWorkflow
from base_workflow import LegacyCustomer
from base_workflow import User
from briefy import common
from conftest import queue_url
from briefy.common import workflow
from briefy.common.workflow import WorkflowPermissionException
from datetime import datetime
from zope.configuration.xmlconfig import XMLConfig

import botocore
import pytest


class TestWorkflow:
    """Tests for Workflow."""

    def setup_class(cls):
        """Setup test class."""
        class MockEndpoint(botocore.endpoint.Endpoint):
            def __init__(self, host, *args, **kwargs):
                super().__init__(queue_url(), *args, **kwargs)

        botocore.endpoint.Endpoint = MockEndpoint

        XMLConfig('configure.zcml', common)()

    def test_workflow_inherits_from_base_workflow(self):
        """Test if a new workflow inherits from base workflow."""
        customer = Customer('12345')
        wf = customer.workflow
        assert isinstance(wf, CustomerWorkflow)
        assert isinstance(wf, workflow.BriefyWorkflow)

    def test_new_customer_gets_history(self):
        """Test if a new customer will receive an initial transition."""
        user = User('12345')
        customer = Customer('12345')
        wf = customer.workflow
        wf.context = user
        history = wf.history
        assert len(history) == 1
        assert history[0]['from'] == ''
        assert history[0]['to'] == 'created'
        assert history[0]['transition'] == ''
        assert datetime.strptime(history[0]['date'][:19], '%Y-%m-%dT%H:%M:%S')

    def test_workflow_state_repr_works(self):
        """Test workfolow __repr__ works"""
        customer = Customer('12345')
        assert 'workflowstate' in repr(customer.workflow.state).lower()

    def test_state_key_unknown_state(self):
        """Raise an error if document is in an unknown state."""
        customer = Customer('12345')
        customer.state = 'foobar'
        with pytest.raises(workflow.WorkflowStateException) as excinfo:
            wf = customer.workflow
            wf.state
        assert 'Unknown state' in str(excinfo.value)

    def test_state_key_not_found(self):
        """Raise an error if document does not have a state_key."""
        customer = {}
        with pytest.raises(workflow.WorkflowStateException) as excinfo:
            CustomerWorkflow(customer)
        assert 'Value for state on' in str(excinfo.value)

    @pytest.mark.parametrize('Customer', [Customer, LegacyCustomer])
    def test_transitions(self, Customer):
        """Test transitions for an object."""
        user = User('12345')
        customer = Customer('12345')
        customer.workflow.context = user
        assert customer.workflow.state == customer.workflow.created
        customer.workflow.submit()
        assert customer.workflow.state == customer.workflow.pending

    @pytest.mark.parametrize('Customer', [Customer, LegacyCustomer])
    def test_transitions_record_message_in_history(self, Customer):
        """Test transitions for an object."""
        user = User('12345')
        customer = Customer('12345')
        customer.workflow.context = user
        msg = 'frtmrglpst!'
        assert customer.workflow.state == customer.workflow.created
        customer.workflow.submit(message=msg)
        assert customer.workflow.state == customer.workflow.pending
        assert customer.workflow.history[-1]['message'] == msg

    def test_transitions_declared_with_multiple_state(self):
        """Test transitions for an object."""
        from briefy.common.workflow import WorkflowTransitionException
        user = User('12345')
        customer = Customer('12345')
        wf = customer.workflow
        wf.context = user
        assert wf.state == wf.created
        wf.submit()
        assert wf.state == wf.pending
        with pytest.raises(WorkflowPermissionException):
            wf.approve()
        user._groups = ('editor',)
        wf.approve()
        assert wf.state == wf.approved
        # This transition from the aproved state is declared as an
        # 'extra_state' in the fixtures and also requires fields and a message

        fields = {'foo': 'bar', 'bar': 'not bar'}
        message = 'Foo bar'

        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.reject()
        assert 'Field foo is required for this transition' in str(excinfo)

        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.reject(fields=fields)
        assert 'Message is required for this transition' in str(excinfo)

        with pytest.raises(WorkflowTransitionException) as excinfo:
            wf.reject(message=message, fields=fields)
        assert 'The value not bar is not acceptable here' in str(excinfo)

        fields['bar'] = 'foo'
        wf.reject(message=message, fields=fields)
        assert wf.state == wf.rejected
        assert customer.foo == 'bar'
        assert customer.bar == 'foo'

    def test_transitions_with_permission_in_decorator_form(self):
        """Test transitions for an object."""
        user = User('12345', groups=('editor',))
        customer = Customer('12345')
        wf = customer.workflow
        wf.context = user
        assert wf.state == wf.created
        wf.submit()
        wf.approve()
        assert wf.state == wf.approved
        # This transition from the aproved state is declared as an
        # 'extra_state' in the fixtures:
        wf.retract()
        assert wf.state == wf.pending

    def test_declarative_permissions_for_state(self):
        user = User('12345', groups=('editor',))
        customer = Customer('12345')
        wf = customer.workflow
        wf.context = user
        wf.submit()
        assert not wf.view
        wf.approve()
        assert wf.state == wf.approved
        assert wf.view

    def test_declarative_permissions_for_role(self):
        user = User('12345', groups=('user',))
        customer = Customer('12345')

        customer.workflow.context = user
        customer.workflow.submit()
        assert not customer.workflow.hot_edit
        user._groups = ('editor',)
        assert customer.workflow.hot_edit

    def test_workflow_property_persists_context(self):
        user = User('12345', groups=('user',))
        customer = Customer('12345')
        customer.workflow.context = user
        assert customer.workflow.context is user

    def test_state_bound_permission_as_decorator(self):
        user = User('12345', groups=('user',))
        customer = Customer('12345')
        wf = customer.workflow
        wf.context = user
        assert not wf.quick_edit
        wf.submit()
        assert wf.quick_edit
        user._groups = ('editor',)
        assert wf.hot_edit

    @pytest.mark.parametrize('Customer', [Customer, LegacyCustomer])
    def test_transition_list(self, Customer):
        """Test list of transitions for an object and an user."""
        user = User('12345')
        customer = Customer('12345')
        wf = customer.workflow
        wf.context = user
        assert len(wf.transitions) == 1
        assert wf.transitions['submit'].title, 'Submit'
        wf.submit()

        # Editor will not be able to transition from cre
        editor = User('23456', groups=('editor', ))
        wf.context = editor
        assert len(wf.transitions) == 2
        assert wf.transitions['approve'].title, 'Approve'
        assert wf.transitions['reject'].title, 'Reject'

    def test_history(self):
        """Test history for an object after some transitions."""
        user = User('12345')
        editor = User('23456', groups=('editor', ))
        customer = Customer('12345')
        wf = customer.workflow
        wf.context = user
        wf.submit()
        wf.context = editor
        wf.approve()
        history = wf.history
        assert len(history) == 3
        assert history[0]['to'] == 'created'
        assert history[1]['to'] == 'pending'
        assert history[2]['to'] == 'approved'
