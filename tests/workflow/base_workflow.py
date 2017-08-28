"""Base tests for briefy.common.workflow."""
from briefy.common.db import Base
from briefy.common.db.mixins import Mixin
from briefy.common.workflow import permission as permission
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import Permission
from briefy.common.workflow import WorkflowState
from briefy.common.workflow import WorkflowStateGroup
from datetime import datetime

import sqlalchemy as sa
import sqlalchemy_utils as sautils


class LegacyCustomerWorkflow(BriefyWorkflow):
    """Workflow for Customer."""

    # Optional name for this workflow
    entity = 'customer'
    initial_state = 'created'
    initial_transition = 'create'

    created = WorkflowState('created', title='Created', description='Customer created')
    pending = WorkflowState('pending', title='Pending', description='Customer waiting for approval')
    approved = WorkflowState('approved', title='Approved', description='Customer approved')
    rejected = WorkflowState('rejected', title='Rejected', description='Customer rejected')

    inactive = WorkflowStateGroup([created, pending, rejected], title='Customer is inactive')
    active = WorkflowStateGroup([approved, ], title='Customer is approved')

    def permissions(self):
        """Return permissions available to current user. A permission can be any hashable token."""
        permissions = super().permissions()
        if not permissions:
            permissions = []
        context = self.context
        document = self.document
        if context:
            user_id = context.user_id
            groups = self.context.groups
            if document.creator == user_id:
                permissions.append('can_submit')
            if 'editor' in groups:
                permissions.append('review')
        return permissions

    @created.transition(pending, 'can_submit', title='Submit')
    def submit(self):
        """Customer asks to be part or our marketplace."""
        pass

    @pending.transition(approved, 'review', title='Approve')
    def approve(self):
        """Editor approve this customer."""
        pass

    @pending.transition(rejected, 'review', title='Reject')
    def reject(self):
        """Editor reject this customer."""
        pass


class CustomerWorkflow(BriefyWorkflow):
    """Workflow for Customer."""

    # Optional name for this workflow
    entity = 'customer'
    initial_state = 'created'

    created = WorkflowState('created', title='Created', description='Customer created')
    pending = WorkflowState('pending', title='Pending', description='Customer waiting for approval')
    approved = WorkflowState('approved', title='Approved', description='Customer approved')
    rejected = WorkflowState('rejected', title='Rejected', description='Customer rejected')

    inactive = WorkflowStateGroup([created, pending, rejected], title='Customer is inactive')
    active = WorkflowStateGroup([approved, ], title='Customer is approved')

    @permission
    def can_submit(self):
        if not self.context or not self.document:
            return False
        return self.document.creator == self.context.id

    @permission
    def review(self):
        return self.context and 'editor' in self.context.groups

    submit = created.transition(pending, 'can_submit', title='Submit')
    # Permissions can be given by instance or name:
    approve = pending.transition(approved, review, title='Approve')
    # extra_states for a transition can be given:
    reject = pending.transition(
        rejected, 'review', title='Reject', extra_states=(approved,),
        require_message=True, required_fields=('foo', 'bar')
    )
    retract = approved.transition(pending, title='Retract')

    @retract.set_permission
    def can_retract(self):
        return self.context and 'editor' in self.context.groups

    # Way to declare 'static' permissions - that apply for pre-declared states
    # and groups. (The "Permission" object can be used just as the "permission" decorator,
    # and will filter out the permission as False even before calling the main method.

    view = Permission().for_states('approved')
    hot_edit = Permission().for_groups('editor')

    @pending.permission
    def quick_edit(self):
        return self.document.creator == self.context.user_id

    @submit
    def submit_hook(self):
        """Body of retract transition"""
        self._retracted_ok = True


class Customer(Mixin, Base):
    """A Customer for Briefy."""

    __tablename__ = 'wfcustomer'

    state = ''
    state_history = None
    creator = None

    _workflow = CustomerWorkflow

    foo = ''
    _bar = ''

    def __init__(self, creator, foo='', bar=''):
        """Initialize a customer."""
        self.id = 'b53f33e2-b2d4-43ef-a8e0-24d2df7a391d'
        self.creator = creator
        self.state_history = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.foo = foo
        self.bar = bar

    @property
    def bar(self) -> str:
        """Bar property."""
        return self._bar

    @bar.setter
    def bar(self, value: str):
        """Bar property setter."""
        if value == 'not bar':
            raise ValueError('The value not bar is not acceptable here')
        self._bar = value

    def to_dict(self, excludes=None, includes=None) -> dict:
        """Return a dictionary with fields and values used by this Class.

        :returns: Dictionary with fields and values used by this Class
        """
        data = super().to_dict(includes=includes, excludes=excludes)
        data['state_history'] = self.state_history
        return data


class LegacyCustomer(Customer):

    __tablename__ = 'wflegacycustomer'

    _workflow_klass = LegacyCustomerWorkflow

    parent_id = sa.Column(
        sautils.UUIDType(),
        sa.ForeignKey('wfcustomer.id'),
        unique=True,
        primary_key=True,
    )


class User:
    """A user."""

    _groups = ()

    def __init__(self, user_id, groups=()):
        """Initialize this class."""
        self.user_id = user_id
        self.id = user_id
        self._groups = groups

    @property
    def groups(self):
        """Return a list of groups for this user."""
        return self._groups
