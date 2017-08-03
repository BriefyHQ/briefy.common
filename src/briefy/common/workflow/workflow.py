"""Briefy base workflow."""
from .exceptions import WorkflowStateException
from .permission import Permission
from .state import AttachedState
from .state import WorkflowState
from .state import WorkflowStateGroup
from .state import WorkflowStates
from .transition import WorkflowTransition
from briefy.common import workflow  # noQA
from briefy.common.db import datetime_utcnow
from briefy.common.event.workflow import WorkflowTransitionEvent
from briefy.common.types import BaseUser
from collections import OrderedDict
from zope.event import notify

import logging
import typing as t
import uuid


logger = logging.getLogger(__name__)


Document = t.Any
UUID_TYPE = t.Union[str, uuid.UUID]


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
            if hasattr(base, '_is_document_workflow') and base._is_document_workflow:
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


class Workflow(metaclass=WorkflowMeta):
    """Base class for workflows."""

    exception_state = WorkflowStateException
    name = ''
    state_key = ''
    history_key = ''
    context_key = ''
    context = None
    initial_state = ''
    initial_transition = ''
    _document_creator_key = 'creator'
    _context_actor_key = 'id'

    def __init__(self, document: Document, context: t.Optional[BaseUser]=None):
        """Initialize the Workflow."""
        self.document = document
        if context:
            self.context = context
        self._state = None
        state = self._get_state()
        initial_state = self.initial_state
        initial_transition = self.initial_transition
        if not state:
            state = initial_state
            self._set_state(state)
            actor = self._get_context_actor(context)
            if not actor:
                actor = self._get_document_creator(document)

            self._update_history(initial_transition, '', state, actor)

        if state not in self.state_values:
            raise self.exception_state('Unknown state')

    def __repr__(self) -> str:
        """Representation of the object."""
        return f'<Workflow {self._name}>'

    @property
    def state_values(self) -> dict:
        """Reverse lookup: value to object."""
        cls = self.__class__
        return getattr(cls, '_state_values', {})

    @property
    def existing_permissions(self) -> dict:
        """Existing permissions on this workflow.

        :return: Dictionary with permissions on this workflow.
        """
        return getattr(self, '_existing_permissions', {})

    @property
    def user(self) -> BaseUser:
        """An alias for context."""
        return self.context

    @user.setter
    def user(self, value: BaseUser):
        """An alias for context."""
        self.context = value

    @property
    def context(self) -> BaseUser:
        """Return context."""
        return self._safe_get(self.document, self.context_key, default=None)

    @context.setter
    def context(self, context: BaseUser):
        self._safe_set(self.document, self.context_key, context)

    @classmethod
    def _safe_get(cls, obj: t.Any, name: str, swallow: bool=True, default: t.Any=None) -> t.Any:
        """Try to get a value from object, given a name."""
        if obj and hasattr(obj, name):
            value = getattr(obj, name)
        elif obj and hasattr(obj.__class__, '__contains__') and name in obj:
            value = obj[name]
        elif swallow:
            value = default
        else:
            raise cls.exception_state(f'Value for {name} on {obj} cannot be read')
        return value

    @classmethod
    def _safe_set(cls, obj: t.Any, name: str, value: t.Any, swallow: bool=True):
        """Try to set a value on a attribute or key named name on an object."""
        if obj and hasattr(obj, name):
            setattr(obj, name, value)
        elif obj and hasattr(obj.__class__, '__contains__') and name in obj:
            obj[name] = value
        elif not swallow:   # pragma: no cover
                            # (execution flow will raise in _safe_get before getting here)
            raise cls.exception_state(f'Value {value} for {name} on {obj} cannot be set')

    @staticmethod
    def _get_safe_actor_info(value: t.Any) -> UUID_TYPE:
        """Clean actor information and return a string."""
        value = value if value else ''
        if isinstance(value, dict):
            value = value.get('id', '')
        return str(value)

    @classmethod
    def _get_document_creator(cls, document: Document) -> UUID_TYPE:
        # Get the creator value from document
        key = cls._document_creator_key
        actor_info = cls._safe_get(document, key)
        return cls._get_safe_actor_info(actor_info)

    @classmethod
    def _get_context_actor(cls, context: BaseUser) -> UUID_TYPE:
        # Get the actor value from context
        key = cls._context_actor_key
        actor_info = cls._safe_get(context, key)
        return cls._get_safe_actor_info(actor_info)

    @classmethod
    def _get_state_value_inner(cls, document: Document) -> str:
        # Get the state value from document
        key = cls.state_key
        return cls._safe_get(document, key, False)

    @classmethod
    def _get_history_value_inner(cls, document: Document) -> t.List:
        # Get the state value from document
        key = cls.history_key
        value = cls._safe_get(document, key, False)
        if not value:
            value = []
        return value

    def _get_state(self) -> str:
        return self._get_state_value_inner(self.document)

    def _set_state(self, value: str):
        # Set state value on document
        document = self.document
        key = self.state_key
        self._safe_set(document, key, value, False)

    def _process_history(self, history: t.List[dict]) -> t.List[dict]:
        """Process workflow history.

        This method exists to clean up workflow history before it is persisted on the
        document attribute.
        """
        cleansed = []
        for entry in history:
            actor = entry['actor']
            if isinstance(actor, dict):
                actor = actor.get('id', '')
            if isinstance(actor, BaseUser) or hasattr(actor, 'id'):
                actor = actor.id
            if isinstance(actor, uuid.UUID):
                actor = str(actor)
            entry['actor'] = actor
            cleansed.append(entry)
        return cleansed

    def _update_history(
            self,
            transition: str,
            state_from: str,
            state_to: str,
            actor: UUID_TYPE='',
            message: str=''
    ):
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
            'actor': str(actor),
            'transition': transition,
            'message': message
        }
        history.append(entry)
        history = self._process_history(history)
        self._safe_set(document, key, history, False)

    @property
    def history(self) -> t.List:
        """Return the history for the document on this workflow."""
        return self._get_history_value_inner(self.document)

    @property
    def state(self) -> t.Union[WorkflowState, AttachedState]:
        """Return the state for the document on this workflow."""
        try:
            state = self.state_values[self._get_state()]
        except KeyError:
            raise self.exception_state('Unknown state')
        return state

    states = WorkflowStates()

    def permissions(self) -> t.Set[str]:
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
            for permission_name, permission in self.existing_permissions.items()
            if permission(self)
        }

    @property
    def transitions(self) -> OrderedDict:
        """All transition available in the current state and context."""
        result = OrderedDict()
        for k, v in self.state._transitions.items():
            permission = self.existing_permissions.get(v.permission, None)
            if permission is None or permission(self):
                result[k] = v
        return result

    def _notify(self, transition: WorkflowTransition) -> None:
        """Notify when a transition happens."""
        pass


class BriefyWorkflow(Workflow):
    """Workflow for an object on Briefy."""

    entity = ''
    """Entity this workflow manages."""

    update_event = None
    """Updated event to fire when document is changed (transitioned) by this workflow."""

    state_key = 'state'
    """Attribute, on the object, to store Workflow state."""

    history_key = 'state_history'
    """Attribute, on the object, to store Workflow history."""

    context_key = 'workflow_context'
    """Attribute storing workflow context (User)."""

    initial_state = 'created'
    """Initial state for the workflow."""

    initial_transition = 'create'
    """Initial transition for the workflow."""

    @property
    def name(self) -> str:
        """Return the name of this workflow."""
        return f'{self.entity}.workflow'

    def _notify(self, transition: WorkflowTransition) -> None:
        """Notify when a WorkflowTransition is executed.

        Trigger a :class:`briefy.common.event.workflow.WorkflowTransitionEvent` event.
        """
        request = None
        obj = self.document
        history = self.history
        entry = history[-1] if history else {}
        logger.info(
            f'Transition {transition.title} was executed for object {obj}',
            extra={'history_entry': entry}
        )
        if hasattr(obj, 'request'):
            request = obj.request
        user = self.context

        # Fire event
        wf_transition_event = WorkflowTransitionEvent(self.document, request, transition, user)

        update_event = self.update_event
        if update_event and request:
            event = update_event(obj, request)
            # this will clear any cache before notify transition
            request.registry.notify(event)
            # also execute the event to dispatch to sqs if needed
            event()

        # Notify using zope.event
        notify(wf_transition_event)

        wf_transition_event()
        super()._notify(transition)
