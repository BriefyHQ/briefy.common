"""Base workflow."""
from .exceptions import WorkflowPermissionException
from .exceptions import WorkflowStateException
from .exceptions import WorkflowTransitionException
from .permission import Permission
from .transition import WorkflowTransition
from briefy.common import workflow  # noQA
from collections import OrderedDict
from enum import Enum

import typing as t
import weakref


permission = Permission
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
    setattr(instance, '_creation_order', _creation_order)
    _creation_order += 1


class AttachedState:
    """A state attached to a workflow."""

    def __init__(self, state: 'workflow.WorkflowState', workflow_: 'workflow.Workflow'):
        """Initialize the state on a workflow."""
        self._parent = weakref.ref(workflow_)
        self.state = state

    def __getattr__(self, attr: str) -> t.Any:
        """Return an attribute on the state."""
        return getattr(self.state, attr)

    def __call__(self) -> bool:
        """Check if value exists in self.state."""
        state = self._parent()._get_state()
        if isinstance(self.state, WorkflowStateGroup):
            return state in self.state.values
        return state == self.value

    def __contains__(self, value: t.Any) -> bool:
        """Check if value exists in self.state."""
        return value in self.state

    def __eq__(self, value: t.Any) -> bool:
        """Compare attached state to a given value."""
        return self.state == value

    def __repr__(self) -> str:
        """Repr of AttachedState."""
        repr_state = repr(self.state).lstrip('<')
        return f'<Attached {repr_state}'


class WorkflowState:
    """A state in a workflow."""

    exception_state = WorkflowStateException
    exception_transition = WorkflowTransitionException
    exception_permission = WorkflowPermissionException

    def __init__(
            self,
            value=None,
            title: str='',
            description: str=''
    ):
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

    def __get__(self, instance: 'workflow.Workflow', owner: t.Any) -> AttachedState:
        """Return am instance of a AttachedState."""
        if not instance:
            return self
        return AttachedState(self, instance)

    def __call__(self) -> None:
        """Call this state."""
        raise self.exception_state('Unattached state')

    def __eq__(self, other: 'WorkflowState') -> bool:
        """Compare this state to other."""
        if isinstance(other, AttachedState):
            other = other.state
        return isinstance(other, WorkflowState) and self.value == other.value

    def __ne__(self, other: 'WorkflowState') -> bool:
        """Compare this state to other."""
        return not self.__eq__(other)

    def transition(
            self,
            state_to: 'WorkflowState',
            permission: t.Optional[Permission]=None,
            name: str=None,
            title: str='',
            description: str='',
            category: str='',
            **kw
    ) -> WorkflowTransition:
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

        transition_obj = WorkflowTransition(
            self,
            state_to,
            permission,
            name=name,
            title=title,
            description=description,
            category=category,
            **kw
        )

        return transition_obj

    def transition_from(
            self,
            state_from: 'WorkflowState',
            permission: Permission,
            **kwargs
    ) -> WorkflowTransition:
        """Reverse of :meth:`WorkflowState.transition`.

        Specifies a transition to this state from one or more source states.
        Does not accept WorkflowStateGroup.
        """
        # TODO: pending rewrite for the new transition system.
        # Will work on the decorator form as it is:
        def inner(f):
            states = [state_from] if isinstance(state_from, WorkflowState) else list(state_from)
            for state in states:
                return state.transition(self, permission, **kwargs)(f)
        return inner

    def permission(
            self,
            func: t.Optional[t.Callable]=None,
            *,
            groups: t.Sequence[t.Union[str, Enum]]=()
    ):
        """Create a Permission bound for this WorkflowState.

        It can be used as a decorator or further filtered down
        just regular Permission objects.
        """
        return Permission(func, groups=groups, states=[self])


class WorkflowStateGroup(WorkflowState):
    """Group of states in a workflow.

    The value parameter is a list of values or WorklowState instances.
    """

    def __init__(
            self,
            value: t.Sequence[t.Union[WorkflowState, str]],
            title: str='',
            description: str=''
    ):
        """Initialize thee WorkflowStateGroup."""
        # Convert all WorkflowState instances to values
        value = [item.value if isinstance(item, WorkflowState) else item for item in value]
        super(WorkflowStateGroup, self).__init__(value, title, description)
        self.values = value

    def __repr__(self) -> str:
        """Representation of a WorkflowStateGroup."""
        return f'<WorkflowStateGroup {self.title}>'

    def __call__(self) -> None:
        """Execute."""
        raise self.exception_state('Unattached state')

    def __contains__(self, state: t.Union[AttachedState, WorkflowState]) -> bool:
        """Check if state is contained in this WorkflowStateGroup."""
        if isinstance(state, AttachedState):
            state = state.state
        if isinstance(state, WorkflowState):
            state = state.value
        return state in self.values

    def transition(self, *args, **kwargs) -> None:
        """Transition."""
        raise TypeError('WorkflowStateGroups cannot have transitions')


State = t.Union[AttachedState, WorkflowState]


class WorkflowStates:
    """Workflow states."""

    def __get__(self, instance: 'workflow.Workflow', owner: t.Any):
        """Return WorkflowStates."""
        self._owner = owner
        return self

    def __iter__(self) -> t.Iterable[State]:
        """Iterate on the states."""
        return iter(self._owner._states_sorted)

    def __getattr__(self, attr: str) -> t.Any:
        """Return a state."""
        try:
            return self[attr]
        except KeyError as exc:
            raise AttributeError from exc

    def __getitem__(self, state_name: str) -> State:
        """Return a state."""
        return self._owner._states[state_name]

    def __len__(self) -> int:
        """Count number of states."""
        return len(self._owner._states_sorted)

    def __repr__(self) -> str:
        """Repr for WorkflowStates."""
        workflow_name = self._owner.__name__
        states = list(self)
        return f'<Allowed states for {workflow_name}: {states}>'
