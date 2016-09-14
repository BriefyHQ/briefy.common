"""Base tests for briefy.common.workflow."""
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState
from briefy.common.workflow import WorkflowStateGroup
from briefy.common.workflow import Permission
from briefy.common.workflow import permission


class LegacyCustomerWorkflow(BriefyWorkflow):
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

    def permissions(self):
        """Return permissions available to current user. A permission can be any hashable token."""
        permissions = super().permissions()
        if not permissions:
            permissions = []
        context = self.context
        document = self.document
        if context:
            user_id = context.user_id
            roles = self.context.roles
            if document.creator == user_id:
                permissions.append('can_submit')
            if 'editor' in roles:
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
        return self.document.creator == self.context.user_id

    @permission
    def review(self):
        return self.context and 'editor' in self.context.roles

    submit = created.transition(pending, 'can_submit', title='Submit')
    # Permissions can be given by instance or name:
    approve = pending.transition(approved, review, title='Approve')
    # extra_states for a transition can be given:
    reject = pending.transition(rejected, 'review', title='Reject', extra_states=(approved,))
    retract = approved.transition(pending, title='Retract')

    @retract.set_permission
    def can_retract(self):
        return self.context and 'editor' in self.context.roles

    # Way to declare 'static' permissions - that apply for pre-declared states
    # and roles. (The "Permission" object can be used just as the "permission" decorator,
    # and will filter out the permission as False even before calling the main method.

    view = Permission().for_states('approved')
    hot_edit = Permission().for_roles('editor')

    @pending.permission
    def quick_edit(self):
        return self.document.creator == self.context.user_id


class Customer:
    """A Customer for Briefy."""

    state = ''
    state_history = None
    creator = None

    _workflow_klass = CustomerWorkflow

    def __init__(self, creator):
        """Initialize a customer."""
        self.creator = creator
        self.state_history = []
        self.workflow = self._workflow_klass(self)


class LegacyCustomer(Customer):
    _workflow_klass = LegacyCustomerWorkflow


class User:
    """A user."""

    _roles = ()

    def __init__(self, user_id, roles=()):
        """Initialize this class."""
        self.user_id = user_id
        self._roles = roles

    @property
    def roles(self):
        """Return a list of roles for this user."""
        return self._roles
