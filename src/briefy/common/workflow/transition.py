"""Base workflow."""
from .exceptions import WorkflowTransitionException
from .permission import Permission
from briefy.common import workflow
from briefy.common.log import logger
from briefy.common.utils.data import inject_call

import typing as t
import weakref


PermissionOrName = t.Union[Permission, str]


class AttachedTransition:
    """A transition attached to a workflow."""

    def __init__(self, transition: 'workflow.WorkflowTransition', workflow: 'workflow.Workflow'):
        """Initialize the transition on a workflow."""
        self.workflow = workflow
        self.transition = transition

    def __getattr__(self, attr: str) -> t.Any:
        """Return an attribute on the transition."""
        return getattr(self.transition, attr)

    def __call__(self, *args, **kw) -> t.Any:
        """Execute the transition."""
        return self.transition(*args, workflow=self.workflow, **kw)

    def __repr__(self) -> str:
        """Repr of AttachedTransition."""
        repr_transition = repr(self.transition).lstrip('<')
        return f'<Attached {repr_transition}'


class WorkflowTransition:
    """Transition between two states in a workflow."""

    _waiting_to_decorate = True

    def __init__(
        self,
        state_from: 'workflow.WorkflowState',
        state_to: 'workflow.WorkflowState',
        permission: t.Optional[PermissionOrName]='',
        name: t.Optional[str]='',
        title: t.Optional[str]='',
        description: t.Optional[str]='',
        category: t.Optional[str]='',
        extra_states: t.Sequence['workflow.WorkflowState']=(),
        require_message: bool=False,
        required_fields: t.Sequence[str]=(),
        optional_fields: t.Sequence[str]=(),
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
        self.optional_fields = optional_fields
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
                optional_fields=optional_fields,
            )

    @property
    def title(self) -> str:
        """Transition title.

        :return: Title of this transition.
        """
        return self._title or self.name.title()

    def set_permission(self, func: t.Callable) -> Permission:
        """Set a permission."""
        if self.permission:
            raise TypeError(f'Conflict: trying to set more than one permission for {self}')
        permission = Permission(func)
        self.permission = permission.name
        return permission

    def guard(self, workflow: 'workflow.Workflow') -> None:
        """Guard for this Transition."""
        name = self.name
        state_from = self.state_from()

        if name not in state_from._transitions:
            raise state_from.exception_transition('Incorrect state for this transition')

        permission = workflow.existing_permissions.get(self.permission, None)
        if permission and not permission(workflow):
            raise state_from.exception_permission('Permission not available')

    def _decorate(self, func: t.Callable) -> 'WorkflowTransition':
        if isinstance(func, WorkflowTransition):
            transition = self
            previous = transition._previous_transition
            while previous:
                transition = previous
            transition._previous_transition = func
            func = self._previous_transition.transition_hook
        if not self.name:
            self.name = func.__name__
            self._name_inherited_from_hook_method = func.__name__

        self.transition_hook = func
        return self

    def _perform_transition(
            self,
            workflow: 'workflow.Workflow',
            message: str='',
            valid_fields: t.Optional[dict]=None,
            fire_event: bool=True
    ) -> None:
        """Perform the transition.

        Following actions are executed here:

            * Set new state on Workflow
            * Update workflow history
            * Call Workflow._notify, to trigger notifications.
        """
        valid_fields = valid_fields if valid_fields else {}
        document = workflow.document
        try:
            document.update(valid_fields)
        except Exception as exc:
            msg = f'Failure when trying to update {document}. Fields {valid_fields}'
            logger.error(msg)
            raise WorkflowTransitionException(str(exc))
        from_name = self.state_from().value
        to_name = self.state_to().value
        workflow._set_state(to_name)
        workflow._update_history(
            self.name,
            from_name,
            to_name,
            message=message
        )
        if fire_event:
            workflow._notify(self)

    def _dispatch(self, *args, workflow: t.Optional['workflow.Workflow']=None, **kw) -> t.Any:
        """Dispatch call to this transition to a sibling transition bound to the appropriate state.

        Will happen when a transition name, or hook function is
        tied to several states in the same workflow
        """
        name = self.name
        state = workflow.state
        correct_transition = state._transitions.get(name, None)
        if correct_transition and correct_transition.name == name:
            return correct_transition(*args, workflow=workflow, **kw)
        raise state.exception_transition('Incorrect state for this transition')

    def __call__(
            self,
            *args,
            workflow: t.Optional['workflow.Workflow']=None,
            message: t.Optional[str]='',
            fields: t.Optional[dict]=None,
            **kw
    ) -> t.Any:
        """Trigger the transition.

        :param fields: An optional 'fields' attribute can be passed in the KW, with a
                       dictionary of fields to be updated on the target document.
        :return: Whatever the transition hook function returns or None
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
            raise RuntimeError('Tried to trigger an unattached transition')

        state = workflow.state
        fields = fields if fields else {}
        required_fields = self.required_fields
        require_message = self.require_message
        fire_event = kw.get('fire_event', True)
        kw['message'] = message
        kw['fields'] = fields
        # If "we are not the transition you are looking for"
        # (i.e., the 'from_state' is a different one, we are
        #  referring to another Transition instance)
        if state is not state_from:
            kw['workflow'] = workflow
            return self._dispatch(*args, **kw)

        # Extract and verify document-updating fields
        # in the transition payload
        if required_fields:
            for key in required_fields:
                if key not in fields:
                    raise state.exception_transition(
                        f'Field {key} is required for this transition.'
                    )

        if require_message and not message:
            raise state.exception_transition('Message is required for this transition')

        self.guard(workflow)

        result = None
        transition_hook = self.transition_hook
        if transition_hook:
            result = inject_call(transition_hook, workflow, *args, **kw)
            updated_message = result.get('message', None) if isinstance(result, dict) else None
            if updated_message:
                message = updated_message

        self._perform_transition(workflow, message, fields, fire_event)

        return result

    def __get__(self, instance, owner) -> t.Union['WorkflowTransition', AttachedTransition]:
        """Return a transition."""
        if not isinstance(instance, workflow.Workflow):
            return self
        return AttachedTransition(self, instance)

    def __repr__(self) -> str:
        """Representation of this object."""
        klass_name = self.__class__.__name__
        name = self.name
        from_name = self.state_from().name
        to_name = self.state_to().name
        return f"<{klass_name}(id='{name}' from='{from_name}' to='{to_name}')>"
