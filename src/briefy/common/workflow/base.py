"""Base workflow."""
from .exceptions import WorkflowPermissionException
from .exceptions import WorkflowStateException
from .exceptions import WorkflowTransitionException
from briefy.common.db import datetime_utcnow
from briefy.common.utils.data import inject_call
from collections import OrderedDict

import weakref


_creation_order = 1


def _set_creation_order(instance):
    """Assign a '_creation_order' sequence to the given instance.

    This allows multiple instances to be sorted in order of creation
    (typically within a single thread; the counter is not thread safe).

    This code is from SQLAlchemy, available here:
    http://www.sqlalchemy.org/trac/browser/lib/sqlalchemy/util/langhelpers.py#L836

    Only recommended for use at app load time.
    """
    global _creation_order
    instance._creation_order = _creation_order
    _creation_order += 1


class WorkflowTransition:
    """Transition between two states in a workflow."""

    _waiting_to_decorate = True

    def __init__(
        self,
        state_from,
        state_to,
        permission=None,
        name=None, title='', description='',
        category='',
        extra_states=(),
        require_message=False,
        required_fields=(),
        **kw
    ):
        """Initialize this workflow transition."""
        if isinstance(permission, Permission):
            permission = permission.name

        self.state_from = weakref.ref(state_from)
        self.state_to = weakref.ref(state_to)
        self.permission = permission
        self.name = name
        self._title = title
        self.description = description
        self.category = category
        self.__dict__.update(kw)
        self.transition_hook = None
        # Attribute to help stacking multiple
        # states reusing the same transition function
        # by stacking transitions used as decorators:
        self._previous_transition = None
        self._name_inherited_from_hook_method = None
        # If require_message is True, the transition will not happen
        # without a message being provided
        self.require_message = require_message
        self.required_fields = required_fields
        if extra_states:
            self._previous_transition = WorkflowTransition(
                extra_states[0],
                state_to,
                permission,
                name,
                title,
                description,
                category,
                extra_states[1:],
                require_message=require_message,
                required_fields=required_fields,
            )

    @property
    def title(self) -> str:
        """Transition title.

        :return: Title of this transition.
        """
        return self._title or self.name.title()

    def set_permission(self, func):
        """Set a permission."""
        if self.permission:
            raise TypeError('Conflict: trying to set more than one permission for {0}'.format(self))
        permission = Permission(func)
        self.permission = permission.name
        return permission

    def guard(self, workflow):
        """Guard for this Transition."""
        state_from = self.state_from()

        if self.name not in state_from._transitions:
            raise state_from.exception_transition('Incorrect state for this transition')

        permission = workflow._existing_permissions.get(self.permission, None)
        if permission and not permission(workflow):
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
            self._name_inherited_from_hook_method = func.__name__

        self.transition_hook = func
        return self

    def _perform_transition(self, workflow, message=None, valid_fields=None, fire_event=True):
        """Perform the transition.

        Following actions are executed here:

            * Set new state on Workflow
            * Update workflow history
            * Call Workflow._notify, to trigger notifications.

        """
        valid_fields = valid_fields if valid_fields else {}
        document = workflow.document
        for key in valid_fields:
            value = valid_fields[key]
            try:
                setattr(document, key, value)
            except Exception as exc:
                raise WorkflowTransitionException(str(exc))
        workflow._set_state(self.state_to().value)
        workflow._update_history(self.name,
                                 self.state_from().value,
                                 self.state_to().value,
                                 message=message)
        if fire_event:
            workflow._notify(self)

    def _dispatch(self, *args, workflow=None, **kw):
        """Dispatch call to this transition to a sibling transition bound to the appropriate state.

        Will happen when a transition name, or hook function is
        tied to several states in the same workflow
        """
        correct_transition = workflow.state._transitions.get(self.name, None)
        if (correct_transition and correct_transition.name == self.name):
            return correct_transition(*args, workflow=workflow, **kw)
        raise workflow.state.exception_transition('Incorrect state for this transition')

    def __call__(self, *args, workflow=None, message=None, fields=None, **kw):
        """Trigger the transition.

        :param fields: An optional 'fields' attribute can be passed in the KW, with a
                       dictionary of fields to be updated on the target document.
        :return: Whatver the transitin hook fucntion returns or None
        """
        if self._waiting_to_decorate:
            if len(args) != 1 or kw:
                raise TypeError('Transitions inside Workflow class bodies '
                                'should only be used as decorators for a transition function')

            func = args[0]

            return self._decorate(func)

        """Mandatory fields to update the document in this transition"""

        state_from = self.state_from()
        if not state_from or not workflow:
            raise RuntimeError('Tried to trigger unattached transition')

        # If "we are not the transition you are looking for"
        # (i.e., the 'from_state' is a different one, we are
        #  referring to another Transition instance)
        if workflow.state is not state_from:
            return self._dispatch(
                *args, workflow=workflow, message=message, fields=fields, **kw
            )

        # Extract and verify document-updating fields
        # in the transition payload
        fields = fields if fields else {}
        required_fields = self.required_fields
        if required_fields:
            for key in required_fields:
                if key not in fields:
                    raise workflow.state.exception_transition(
                        'Field {field} is required for this transition.'.format(
                            field=key
                        )
                    )

        if self.require_message and not message:
            raise workflow.state.exception_transition('Message is required for this transition')

        self.guard(workflow)

        if self.transition_hook:
            # 'fields' are included in the kw and also add message

            result = inject_call(
                self.transition_hook,
                workflow,
                *args,
                message=message,
                fields=fields,
                **kw
            )
        else:
            result = None

        updated_message = result.get('message', None) if isinstance(result, dict) else None
        if updated_message:
            message = updated_message
        fire_event = kw.get('fire_event', True)
        self._perform_transition(workflow, message, fields, fire_event)

        return result

    def __get__(self, instance, owner):
        """Return a transition."""
        if not isinstance(instance, Workflow):
            return self
        return AttachedTransition(self, instance)

    def __repr__(self) -> str:
        """Representation of this object."""
        return (
            """<{0}(id='{1}' from='{2}' to='{3}')>""").format(
                self.__class__.__name__,
                self.name,
                self.state_from().name,
                self.state_to().name
        )


class AttachedState:
    """A state attached to a workflow."""

    def __init__(self, state, workflow):
        """Initialize the state on a warkflow."""
        self._parent = weakref.ref(workflow)
        self.state = state

    def __getattr__(self, attr):
        """Return an attribute on the state."""
        return getattr(self.state, attr)

    def __call__(self):
        """Check if value exists in self.state."""
        if isinstance(self.state, WorkflowStateGroup):
            return self._parent()._get_state() in self.state.values
        return self._parent()._get_state() == self.value

    def __contains__(self, value):
        """Check if value exists in self.state."""
        return value in self.state

    def __eq__(self, value):
        """Compare attached state to a given value."""
        return self.state == value

    def __repr__(self):
        """Repr of AttachedState."""
        return '<Attached {0}'.format(repr(self.state).lstrip('<'))


class AttachedTransition:
    """A transition attached to a workflow."""

    def __init__(self, transition, workflow):
        """Initialize the transition on a warkflow."""
        self.workflow = workflow
        self.transition = transition

    def __getattr__(self, attr):
        """Return an attribute on the transition."""
        return getattr(self.transition, attr)

    def __call__(self, *args, **kw):
        """Execute the transition."""
        return self.transition(*args, workflow=self.workflow, **kw)

    def __repr__(self):
        """Repr of AttachedTransition."""
        return '<Attached {0}'.format(repr(self.transition).lstrip('<'))


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
        self._title = title
        self.description = description
        self.__doc__ = description
        self._parent = None
        self._transitions = OrderedDict()
        _set_creation_order(self)

    @property
    def title(self) -> str:
        """Title of the state."""
        return self._title or self.name.title()

    def __repr__(self) -> str:
        """Representation of this state."""
        return '<WorkflowState {title}>'.format(title=self.title)

    def __get__(self, instance, owner):
        """Return am instance of a AttachedState."""
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

    def transition(
            self, state_to, permission=None, name=None, title='', description='', category='', **kw
    ):
        """Declare a decorator for transition functions.

        Usage- on a WorkflowBody,  use either::

            submit = workflow_state.transition(state_to, permission, ...)

        or::

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
        # TODO: pending rewrite for the new transition system.
        # Will work on the decorator form as it is:
        def inner(f):
            states = [state_from] if isinstance(state_from, WorkflowState) else state_from
            for state in states:
                return state.transition(self, permission, **kwargs)(f)
        return inner

    def permission(self, func=None, *, groups=None):
        """Create a Permission bound for this WorkflowState.

        It can be used as a decorator or further filtered down
        just regular Permission objetcs.
        """
        return Permission(func, groups=groups, states=self)


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
        return '<WorkflowStateGroup {0}>'.format(self.title)

    def __call__(self):
        """Execute."""
        raise self.exception_state('Unattached state')

    def __contains__(self, state):
        """Check if state is contained in this WorkflowStateGroup."""
        if isinstance(state, AttachedState):
            state = state.state
        if isinstance(state, WorkflowState):
            state = state.value
        return state in self.values

    def transition(self, *args, **kwargs):
        """Transition."""
        raise TypeError('WorkflowStateGroups cannot have transitions')


class Permission:
    """Class used as a decorator to change a workflow method in a dynamic permission.

    The method should check whether in the current context (available as self.context),
    and the current document (self.document)
    the permission it represents is granted. The method should
    take no parameters other than 'self' (the Workflow instance)

    A permission with the method name is made available to the current workflow
    and will exist anytime the decorated method returns a truthy value::

        class MyWorkflow(Workflow):
            @permission
            def read(self):
                return self.context and 'editor' in self.context.groups

    A non-decorator declaration can also be made by doing::

        class MyWorkflow(Workflow):
            read = Permission().for_groups('g:editors')
            publish = Permission().for_groups('g:editors').for_state('pendding')

    Permissions are checked by transitions inside workflow.states -
    any transition requires a permission, which will be checked by its name.

    Moreover - permissions are also used by views when the workflowed method is
    used by our webservices. In the briefy.ws package there is (TBD) a
    "with_workflow" class decorator that dynamically attaches these permissions
    to objects in a way the default authorization policy for Pyramid understands
    them.
    """

    _name = None
    _waiting_to_decorate = True

    def __init__(self, permission_method=None, states=None, groups=None):
        """Initialize the permission."""
        if isinstance(states, (str, WorkflowState)):
            states = [states]
        self.states = list(states) if states else list()
        self.groups = self._process_groups(groups)
        self(permission_method)

    def _process_groups(self, groups=()) -> set:
        """Process a list of groups and return a set with strings."""
        processed = set()
        groups = groups if groups else ()
        for group in groups:
            processed.add(
                group.value if hasattr(group, 'value') else group
            )
        return processed

    def _filtered_method(self, workflow):
        """Filtered methods.

        This is separated fom __call__ so that it can be decorated by calls to
        'for_groups' and 'for_state'.

        The Always True permission is used if no actual method is ever given, allowing
        for static or filtered only permissions.
        """
        return self.method(workflow) if self.method else True

    @property
    def name(self):
        """Name of the permission."""
        return self._name or self.method.__name__

    __name__ = name

    def __call__(self, workflow):
        """Decorate the workflow."""
        # _waiting_to_decorate is switched off on Workflow class creation,
        # at the metaclass
        if self._waiting_to_decorate:
            self.method = workflow
            return self

        if self.groups:
            if not workflow.context:
                return False
            if not self.groups.intersection(workflow.context.groups):
                return False

        if self.states:
            # This checking must be done here because WorkflowState's names are
            # lazily bound at the Workflow metaclass
            if isinstance(self.states, list):
                self.states = {state.value if isinstance(state, WorkflowState) else state
                               for state in self.states}
            if workflow.state.value not in self.states:
                return False

        if self.method:
            return self.method(workflow)
        return True

    def for_groups(self, *args):
        """Apply permission just to some groups.

        Chain call that decorates this permission so that it is filtered restricting the
        permission to the groups passed in.
        """
        args = self._process_groups(args)
        self.groups.update(args)
        return self

    def for_states(self, *args):
        """Apply permission just for some states.

        Chain call that decorates this permission so that
        it is filtered restricing the permission to the states passed in.
        """
        # self.states can't be a set at this point because
        # states may be refereced by objects  - with late
        # name binding) - that are unhashable
        self.states.extend(args)
        return self

    def __get__(self, instance, owner):
        """Get the permission."""
        if instance is None:
            return self
        return self(instance)


permission = Permission


class WorkflowMeta(type):
    """Base Metaclass for Workflow."""

    def __new__(cls, cls_name, bases, attrs):
        """Constructor."""
        attrs['_is_document_workflow'] = True
        attrs['_name'] = cls_name
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

        transition_disambiguation = {}
        for name, value in attrs.items():

            if isinstance(value, WorkflowState):
                state = value
                state.name = name
                if isinstance(state, WorkflowStateGroup):
                    attrs['_state_groups'][name] = state
                else:
                    attrs['_states'][name] = state
                    # A group doesn't have a single value, so don't add groups
                    attrs['_state_values'][state.value] = state

            elif isinstance(value, WorkflowTransition):
                transition = value
                while transition:
                    hook = transition.transition_hook
                    doc = hook.__doc__ if hook else transition.__doc__
                    transition.__doc__ = doc
                    if not transition.name or transition._name_inherited_from_hook_method:
                        if name != transition._name_inherited_from_hook_method:
                            transition.name = name
                    # Bind transition to the states transitions by name,
                    # as only at this point we are sure of its name
                    transition.state_from()._transitions[transition.name] = transition
                    transition._waiting_to_decorate = False

                    transition_disambiguation.setdefault(id(transition), (transition, {name}))
                    transition_disambiguation[id(transition)][1].add(name)

                    transition = transition._previous_transition

            elif isinstance(value, Permission):
                permission = value
                # This mechanism attributes names so that
                # for permissions that are static, or filtered by state or groups
                # there is no need to set a stub decorated method:
                if permission.method is None:
                    permission._name = name
                else:
                    permission.__doc__ = permission.method.__doc__

                # Activate the permission callable:
                permission._waiting_to_decorate = False

                attrs['_existing_permissions'][value.name] = permission

        # normalize transitions:
        transition_names_to_erase = {}
        for transition_id, data in transition_disambiguation.items():
            transition, names = data
            if len(names) == 1:
                continue
            for name in names:
                if name == transition.transition_hook.__name__:
                    transition_names_to_erase[name] = transition
        for name, transition in transition_names_to_erase.items():
            state = transition.state_from()
            try:
                del state._transitions[name]
            except KeyError:
                # Due to out of order processing of attrs,
                # the second name may never have been added to the transition
                pass
            del attrs[name]

        attrs['_states_sorted'] = sorted(attrs['_states'].values(),
                                         key=lambda s: s._creation_order)
        return super(WorkflowMeta, cls).__new__(cls, cls_name, bases, attrs)


class WorkflowStates:
    """Workflow states."""

    def __get__(self, instance, owner):
        """Return WorkflowStates."""
        self._owner = owner
        return self

    def __iter__(self):
        """Iterate on the states."""
        return iter(self._owner._states_sorted)

    def __getattr__(self, state_name):
        """Return a state."""
        try:
            return self[state_name]
        except KeyError as exc:
            raise AttributeError from exc

    def __getitem__(self, state_name):
        """Return a state."""
        return self._owner._states[state_name]

    def __len__(self):
        """Count number of states."""
        return len(self._owner._states_sorted)

    def __repr__(self):
        """Repr for WorkflowStates."""
        return '<Allowed states for {0}: {1}>'.format(self._owner.__name__, list(self))


class Workflow(metaclass=WorkflowMeta):
    """Base class for workflows."""

    exception_state = WorkflowStateException
    name = None
    state_key = None
    history_key = None
    context_key = None
    initial_state = None
    _document_creator_key = 'creator'
    _context_actor_key = 'id'

    def __init__(self, document, context=None):
        """Initialize the Workflow."""
        self.document = document
        if context:
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
        return '<Workflow {0}>'.format(self._name)

    @property
    def user(self):
        """Just an alias for context."""
        return self.context

    @user.setter
    def user(self, value):
        self.context = value

    @property
    def context(self):
        """Return context."""
        return self._safe_get(self.document, self.context_key, default=None)

    @context.setter
    def context(self, context):
        return self._safe_set(self.document, self.context_key, context)

    @classmethod
    def _safe_get(cls, obj, name, swallow=True, default=None):
        """Try to get a value from object, given a name."""
        if obj and hasattr(obj, name):
            value = getattr(obj, name)
        elif obj and hasattr(obj.__class__, '__contains__') and name in obj:
            value = obj[name]
        elif swallow:
            value = default
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

    def _update_history(self, transition, state_from, state_to,
                        actor=None, message=None):
        now = datetime_utcnow().isoformat()
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
            'transition': transition,
            'message': message
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
        """Return permissions available in the current context.

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
        result = OrderedDict()
        for k, v in self.state._transitions.items():
            permission = self._existing_permissions.get(v.permission, None)
            if permission is None or permission(self):
                result[k] = v
        return result

    def _notify(self, transition):
        """Notify when a transition happens."""
        pass
