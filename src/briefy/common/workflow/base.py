"""Base workflow."""
from .exceptions import WorkflowPermissionException
from .exceptions import WorkflowStateException
from .exceptions import WorkflowTransitionException
from collections import OrderedDict
from datetime import datetime
from functools import wraps

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

    def __init__(self, name, title='', description='', category='',
                 permission='', state_from=None, state_to=None, **kwargs):
        """Initialize a workflow transition."""
        self.name = name
        self.title = title
        self.description = description
        self.category = category
        self.permission = permission
        self.state_from = weakref.ref(state_from)
        self.state_to = weakref.ref(state_to)
        self.__dict__.update(kwargs)


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

    def attach(self, workflow):
        """Attach this workflow state to a workflow instance."""
        # Attaching works by creating a new copy of the state with _parent
        # now referring to the workflow instance.
        newstate = self.__class__(self.value, self.title, self.description)
        newstate.name = self.name
        newstate._parent = weakref.ref(workflow)
        newstate._transitions = self._transitions
        return newstate

    def __repr__(self):
        """Representation of this state."""
        return '<WorkflowState {}>'.format(self.title)

    def __call__(self):
        """Call this state."""
        if self._parent is None or self._parent() is None:
            raise self.exception_state('Unattached state')
        return self._parent()._get_state() == self.value

    def __eq__(self, other):
        """Compare this state to other."""
        return isinstance(other, WorkflowState) and self.value == other.value

    def __ne__(self, other):
        """Compare this state to other."""
        return not self.__eq__(other)

    def transition(self, state_to, permission,
                   name=None, title='', description='', category='', **kw):
        """Decorator for transition functions."""
        def inner(f):
            if hasattr(f, '_workflow_transition_inner'):
                f = f._workflow_transition_inner

            workflow_name = name or f.__name__

            @wraps(f)
            def decorated_function(workflow, *args, **kwargs):
                # Perform tests: is state correct? Is permission available?
                if workflow_name not in workflow.state._transitions:
                    raise self.exception_transition('Incorrect state')
                t = workflow.state._transitions[workflow_name]
                if t.permission and (t.permission not in workflow.permissions()):
                    raise self.exception_permission('Permission not available')
                result = f(workflow, *args, **kwargs)
                state_from = t.state_from().value
                state_to = t.state_to().value
                workflow._set_state(state_to)
                workflow._update_history(t.title, state_from, state_to)
                workflow._notify(t)
                return result

            t = WorkflowTransition(name=workflow_name,
                                   title=title,
                                   description=description,
                                   category=category,
                                   permission=permission,
                                   state_from=self,
                                   state_to=state_to,
                                   **kw)
            self._transitions[workflow_name] = t
            decorated_function._workflow_transition_inner = f
            return decorated_function
        return inner

    def transition_from(self, state_from, permission, **kwargs):
        """Reverse of :meth:`WorkflowState.transition`.

        Specifies a transition to this state from one or more source states.
        Does not accept WorkflowStateGroup.
        """
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
        """Return the state value."""
        if self._parent is None or self._parent() is None:
            raise self.exception_state('Unattached state')
        return self._parent()._getStateValue() in self.value

    def transition(self, *args, **kwargs):
        """Transition."""
        raise SyntaxError('WorkflowStateGroups cannot have transitions')


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
        for base in bases:
            if hasattr(base,
                       '_is_document_workflow') and base._is_document_workflow:
                attrs['_states'].update(base._states)
                attrs['_state_groups'].update(base._state_groups)
                attrs['_state_values'].update(base._state_values)

        for statename, stateob in attrs.items():
            if isinstance(stateob, WorkflowState):
                stateob.name = statename
                if isinstance(stateob, WorkflowStateGroup):
                    attrs['_state_groups'][statename] = stateob
                else:
                    attrs['_states'][statename] = stateob
                    # A group doesn't have a single value, so don't add groups
                    attrs['_state_values'][stateob.value] = stateob

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
        if state not in self._state_values:
            raise self.exception_state('Unknown state')
        # Attach states to self. Make copy and iterate:
        # This code is used just to make it possible to test
        # if a state is active by calling it: workflow.draft(), etc
        for statename, stateob in list(self._states.items()):
            attached = stateob.attach(self)
            setattr(self, statename, attached)
            self._states[statename] = attached
            self._state_values[attached.value] = attached
        for statename, stateob in list(self._state_groups.items()):
            attached = stateob.attach(self)
            setattr(self, statename, attached)
            self._state_groups[statename] = attached

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
        elif not swallow:
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
        """Permission available in the current context.

        This method must be overridden by subclasses. Context is available as self.context,
        set when the workflow was initialized for the document. It is not
        passed as a parameter to this method.
        """
        return []

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
