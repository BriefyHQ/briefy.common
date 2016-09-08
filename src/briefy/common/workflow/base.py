"""Base workflow."""
from .exceptions import WorkflowPermissionException
from .exceptions import WorkflowStateException
from .exceptions import WorkflowTransitionException
from collections import OrderedDict
from datetime import datetime

import pytz
import weakref


_creation_order = 1


def _set_creation_order(instance):
    """Assign a '_creation_order' sequence to the given instance.

    This allows multiple instances to be sorted in order of creation
    (typically within a single thread; the counter is not threadsafe).

    This code is from SQLAlchemy, available here:
    http://www.sqlalchemy.org/trac/browser/lib/sqlalchemy/util/langhelpers.py#L836

    Only recommended for use at app load time.
    """
    global _creation_order
    instance._creation_order = _creation_order
    _creation_order += 1


class WorkflowTransition(object):
    """Transition between states."""

    _waiting_to_decorate = True

    def __init__(self, state_from, state_to,
                 permission=None,
                 name=None, title='', description='',
                 category='',
                 extra_states=(),
                 **kw):
        """Initialize a workflow transition."""

        if isinstance(permission, Permission):
            permission = permission.name

        self.state_from = weakref.ref(state_from)
        self.state_to = weakref.ref(state_to)
        self.permission = permission
        self.name = name
        self.title = title
        self.description = description
        self.category = category
        self.__dict__.update(kw)
        self.transition_hook = None
        # Attribute to help stacking multiple
        # states reusing the same transiction function
        # by stacking transitions used as decorators:
        self._previous_transition = None
        if extra_states:
            self._previous_transition = WorkflowTransition(
                extra_states[0], state_to, permission, name, title, description, category,
                extra_states[1:]
            )

    def set_permission(self, func):
        if self.permission:
            raise TypeError('Conflict: trying to set more than one permission for {}'.format(self))
        permission = Permission(func)
        self.permission = permission.name
        return permission

    def guard(self, workflow):
        state_from = self.state_from()

        if self.name not in state_from._transitions:
            raise state_from.exception_transition('Incorrect state for this transition')

        if self.permission and (self.permission not in workflow.permissions()):
            raise state_from.exception_permission('Permission not available')

    def _decorate(self, func):
        if isinstance(func, WorkflowTransition):
            transition = self
            while transition._previous_transition:
                transition = transition._previous_transition
            transition._previous_transition = func
            func = self._previous_transition.transition_hook
        if not self.name:
            self.name = func.__name__

        self.transition_hook = func
        return self

    def _perform_transition(self, workflow):
        """ Where all the magic really happens """
        workflow._set_state(self.state_to().value)
        workflow._update_history(self.title,
                                 self.state_from().value,
                                 self.state_to().value)
        workflow._notify(self)

    def _dispatch(self, *args, workflow=None, **kw):
        """ Dispatch a call to this transition to a sibling transition
        bound to the appropriate state.
        Will happen when a transition name, or hook function is
        tied to several states in the same workflow
        """

        correct_transition = workflow.state._transitions.get(self.name, None)
        if (correct_transition and
                correct_transition.name == self.name):
            return correct_transition(*args, workflow=workflow, **kw)
        raise workflow.state.exception_transition('Incorrect state for this transition')

    def __call__(self, *args, workflow=None, **kw):
        if self._waiting_to_decorate:
            if len(args) != 1 or kw:
                raise TypeError("Transitions inside Workflow class bodies "
                                "should only be used as decorators for a transition function")

            func = args[0]

            return self._decorate(func)

        state_from = self.state_from()
        if not state_from or not workflow:
            raise RuntimeError('Tried to trigger unnatached transition')

        if workflow.state is not state_from:
            return self._dispatch(*args, workflow=workflow, **kw)

        self.guard(workflow)

        if self.transition_hook:
            result = self.transition_hook(workflow, *args, **kw)
        else:
            result = None

        self._perform_transition(workflow)

        return result

    def __get__(self, instance, owner):
        if not isinstance(instance, Workflow):
            return self
        return AttachedTransition(self, instance)


class AttachedState:
    def __init__(self, state, workflow):
        self._parent = weakref.ref(workflow)
        self.state = state

    def __getattr__(self, attr):
        return getattr(self.state, attr)

    def __call__(self):
        if isinstance(self.state, WorkflowStateGroup):
            return self._parent()._get_state() in self.state.values
        return self._parent()._get_state() == self.value

    def __contains__(self, value):
        return value in self.state

    def __eq__(self, value):
        return self.state == value

    def __repr__(self):
        return '<Attached {}'.format(repr(self.state).lstrip('<'))


class AttachedTransition:
    def __init__(self, transition, workflow):
        self.workflow = workflow
        self.transition = transition

    def __getattr__(self, attr):
        return getattr(self.state, attr)

    def __call__(self, *args, **kw):
        return self.transition(*args, workflow=self.workflow, **kw)

    def __repr__(self):
        return '<Attached {}'.format(repr(self.transition).lstrip('<'))


class WorkflowState(object):
    """A state in a workflow."""

    exception_state = WorkflowStateException
    exception_transition = WorkflowTransitionException
    exception_permission = WorkflowPermissionException

    def __init__(self, value=None, title='', description=''):
        """Initialize the WorkflowState."""
        self.value = value
        self.values = [value]
        self.name = None  # Not named yet
        self.title = title
        self.description = description
        self._parent = None
        self._transitions = OrderedDict()
        _set_creation_order(self)

    def __repr__(self):
        """Representation of this state."""
        return '<WorkflowState {}>'.format(self.title)

    def __get__(self, instance, owner):
        if not instance:
            return self
        return AttachedState(self, instance)

    def __call__(self):
        """Call this state."""
        raise self.exception_state('Unattached state')

    def __eq__(self, other):
        """Compare this state to other."""
        if isinstance(other, AttachedState):
            other = other.state
        return isinstance(other, WorkflowState) and self.value == other.value

    def __ne__(self, other):
        """Compare this state to other."""
        return not self.__eq__(other)

    def transition(self, state_to, permission=None,
                   name=None, title='', description='', category='', **kw):
        """Declaring or decorator for transition functions

        Usage- on a WorkflowBody,  use either:

        submit = workflow_state.transition(state_to, permission, ...)

        or:

        @workflow_state.transition(state_to, permission, ...):
        def submit(self):
            # code to run when transition happens

        """

        # the transition will be set in self._transitions
        # on the Workflow class creation at it's metaclass.__new__

        transition_obj = WorkflowTransition(self, state_to, permission,
                                            name=name,
                                            title=title,
                                            description=description,
                                            category=category,
                                            **kw)

        return transition_obj

    def transition_from(self, state_from, permission, **kwargs):
        """Reverse of :meth:`WorkflowState.transition`.

        Specifies a transition to this state from one or more source states.
        Does not accept WorkflowStateGroup.
        """
        # TODO: pending rewrit for the new transition system.
        # Will work on the decorator form as it is:
        def inner(f):
            states = [state_from] if isinstance(state_from, WorkflowState) else state_from
            for state in states:
                return state.transition(self, permission, **kwargs)(f)
        return inner


class WorkflowStateGroup(WorkflowState):
    """Group of states in a workflow.

    The value parameter is a list of values or WorklowState instances.
    """

    def __init__(self, value, title='', description=''):
        """Initialize thee WorkflowStateGroup."""
        # Convert all WorkflowState instances to values
        value = [item.value if isinstance(item, WorkflowState) else item for item in value]
        super(WorkflowStateGroup, self).__init__(value, title, description)
        self.values = value

    def __repr__(self):
        """Representation of a WorkflowStateGroup."""
        return '<WorkflowStateGroup {}>'.format(self.title)

    def __call__(self):
        raise self.exception_state('Unattached state')

    def __contains__(self, state):
        if isinstance(state, AttachedState):
            state = state.state
        if isinstance(state, WorkflowState):
            state = state.value
        return state in self.values

    def transition(self, *args, **kwargs):
        """Transition."""
        raise TypeError('WorkflowStateGroups cannot have transitions')


class Permission:
    """
    Class used as a decorator to change a workflow method in a
    dynamic permission - the method should check
    whether in the current context (available as self.context),
    and the current document (self.document)
    the permission it represents is granted. The method should
    take no parameters other than 'self' (the Workflow instance)

    A permission with the method name is made available to the current workflow
    and will exist anytime the decorated method returns a truthy value.

    Permissions are checked by transitions inside workflow.states -
    any transition requires a permission, which will be checked by its name.
    """

    _name = None

    def __init__(self, permission_method):
        self.method = permission_method

    @property
    def name(self):
        return self._name or self.method.__name__

    __name__ = name

    def __call__(self, workflow):
        return self.method(workflow)

permission = Permission


class BaseWorkflow(type):
    """Base Metaclass for Workflow."""

    def __new__(cls, name, bases, attrs):
        """Constructor."""
        attrs['_is_document_workflow'] = True
        attrs['_name'] = name
        attrs['_states'] = {}  # state_name: object
        attrs['_state_groups'] = {}  # state_group: object
        attrs['_state_values'] = {}  # Reverse lookup: value to object
        # If any base class contains _states, _state_groups or _state_values,
        # extend them
        attrs['_existing_permissions'] = {}
        for base in bases:
            if hasattr(base,
                       '_is_document_workflow') and base._is_document_workflow:
                attrs['_states'].update(base._states)
                attrs['_state_groups'].update(base._state_groups)
                attrs['_state_values'].update(base._state_values)
                attrs['_existing_permissions'].update(base._existing_permissions)

        for key, value in attrs.items():
            if isinstance(value, WorkflowState):
                statename, stateob = key, value
                stateob.name = statename
                if isinstance(stateob, WorkflowStateGroup):
                    attrs['_state_groups'][statename] = stateob
                else:
                    attrs['_states'][statename] = stateob
                    # A group doesn't have a single value, so don't add groups
                    attrs['_state_values'][stateob.value] = stateob
            elif isinstance(value, WorkflowTransition):
                name, transition = key, value
                while transition:
                    if not transition.name:
                        transition.name = name
                    # Bind transition to the states transitions by name,
                    # as only at this point we are sure of its name
                    transition.state_from()._transitions[transition.name] = transition
                    transition._waiting_to_decorate = False
                    transition = transition._previous_transition

            elif isinstance(value, Permission):
                attrs['_existing_permissions'][value.name] = value

        attrs['_states_sorted'] = sorted(attrs['_states'].values(),
                                         key=lambda s: s._creation_order)
        return super(BaseWorkflow, cls).__new__(cls, name, bases, attrs)


class WorkflowStates:
    def __get__(self, instance, owner):
        self._owner = owner
        return self

    def __iter__(self):
        return iter(self._owner._states_sorted)

    def __getattr__(self, state_name):
        try:
            return self[state_name]
        except KeyError as exc:
            raise AttributeError from exc

    def __getitem__(self, state_name):
        return self._owner._states[state_name]

    def __len__(self):
        return len(self._owner._states_sorted)

    def __repr__(self):
        return "<Allowed states for {}: {}>".format(self._owner.__name__, list(self))


class Workflow(metaclass=BaseWorkflow):
    """Base class for workflows."""

    exception_state = WorkflowStateException
    name = None
    state_key = None
    history_key = None
    initial_state = None
    _document_creator_key = 'creator'
    _context_actor_key = 'user_id'

    def __init__(self, document, context=None):
        """Initialize the Workflow."""
        self.document = document
        self.context = context
        self._state = None
        state = self._get_state()
        if not state:
            state = self.initial_state
            self._set_state(state)
            actor = self._get_context_actor(context)
            if not actor:
                actor = self._get_document_creator(document)
            self._update_history('', '', state)
        if state not in self.__class__._state_values:
            raise self.exception_state('Unknown state')

    def __repr__(self):
        """Representation of the object."""
        return '<Workflow {}>'.format(self._name)

    @classmethod
    def _safe_get(cls, obj, name, swallow=True):
        """Try to get a value from object, given a name."""
        if obj and hasattr(obj, name):
            value = getattr(obj, name)
        elif obj and hasattr(obj.__class__, '__contains__') and name in obj:
            value = obj[name]
        elif swallow:
            value = None
        else:
            raise cls.exception_state(
                'Value for {name} on {obj} cannot be read'.format(
                    name=name,
                    obj=str(obj)
                )
            )
        return value

    @classmethod
    def _safe_set(cls, obj, name, value, swallow=True):
        """Try to set a value on a attribute or key named name on an object."""
        if obj and hasattr(obj, name):
            setattr(obj, name, value)
        elif obj and hasattr(obj.__class__, '__contains__') and name in obj:
            obj[name] = value
        elif not swallow:   # pragma: no cover
                            # (execution flow will raise in _safe_get before getting here)
            raise cls.exception_state(
                'Value {value} for {name} on {obj} cannot be set'.format(
                    value=value,
                    name=name,
                    obj=str(obj)
                )
            )

    @classmethod
    def _get_document_creator(cls, document):
        # Get the creator value from document
        key = cls._document_creator_key
        return cls._safe_get(document, key)

    @classmethod
    def _get_context_actor(cls, context):
        # Get the actor value from context
        key = cls._context_actor_key
        return cls._safe_get(context, key)

    @classmethod
    def _get_state_value_inner(cls, document):
        # Get the state value from document
        key = cls.state_key
        return cls._safe_get(document, key, False)

    @classmethod
    def _get_history_value_inner(cls, document):
        # Get the state value from document
        key = cls.history_key
        value = cls._safe_get(document, key, False)
        if not value:
            value = []
        return value

    def _get_state(self):
        return self._get_state_value_inner(self.document)

    def _set_state(self, value):
        # Set state value on document
        document = self.document
        key = self.state_key
        self._safe_set(document, key, value, False)

    def _update_history(self, transition, state_from, state_to, actor=None):
        now = datetime.now(tz=pytz.timezone('UTC')).isoformat()
        document = self.document
        context = self.context
        if context and not actor:
            actor = self._get_context_actor(context)
        key = self.history_key
        history = self._get_history_value_inner(document)
        entry = {
            'from': state_from,
            'to': state_to,
            'date': now,
            'actor': actor,
            'transition': transition
        }
        history.append(entry)
        self._safe_set(document, key, history, False)

    @property
    def history(self):
        """Return the history for the document on this workflow."""
        return self._get_history_value_inner(self.document)

    @property
    def state(self):
        """Return the state for the document on this workflow."""
        try:
            state = self._state_values[self._get_state()]
        except KeyError:
            raise self.exception_state('Unknown state')
        return state

    states = WorkflowStates()

    def permissions(self):
        """Permissions available in the current context.

        This method can be overriden by subclasses.
        This allows one to return string (or other hashable token)
        permissions directly, instead of having 'Permission'
        objects as code in the workflow classes.

        Context is available as self.context,
        set when the workflow was initialized for the document. It is not
        passed as a parameter to this method.

        :rtype: set
        """

        return {
            permission_name
            for permission_name, permission in self._existing_permissions.items()
            if permission(self)
        }

    @property
    def transitions(self):
        """All transition available in the current state and context."""
        permissions = self.permissions()
        result = OrderedDict()
        for k, v in self.state._transitions.items():
            if v.permission is None or v.permission in permissions:
                result[k] = v
        return result

    def _notify(self, transition):
        """Notify when a transition happens."""
        pass
