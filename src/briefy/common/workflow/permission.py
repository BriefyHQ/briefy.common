"""Workflow permission."""
from briefy.common import workflow  # noQA
from enum import Enum

import typing as t


WorkflowState = t.Union[str, 'workflow.WorkflowState']
OptionalCallable = t.Optional[t.Callable]


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
    _method = None

    def __init__(
        self,
        permission_method: t.Optional[t.Callable]=None,
        states: t.Sequence[WorkflowState]=(),
        groups: t.Sequence[t.Union[str, Enum]]=()
    ):
        """Initialize the permission."""
        if not isinstance(states, (list, tuple)):
            states = [states]
        self.states = list(states)
        self.groups = self._process_groups(groups)
        self(permission_method)

    @property
    def name(self) -> str:
        """Name of the permission."""
        return self._name or self.method.__name__

    __name__ = name

    @property
    def method(self) -> t.Union[t.Callable, 'workflow.Workflow']:
        """Method to implement additional permission checking."""
        return self._method

    @method.setter
    def method(self, value: t.Union[t.Callable, 'workflow.Workflow']):
        """Method to implement additional permission checking."""
        self._method = value

    def _process_groups(self, groups: t.Sequence[t.Union[str, Enum]]=()) -> t.Set[str]:
        """Process a list of groups and return a set with strings."""
        processed = set()
        groups = groups if groups else ()
        for group in groups:
            processed.add(group.value if hasattr(group, 'value') else group)
        return processed

    def _filtered_method(self, workflow_: 'workflow.Workflow'):
        """Filtered methods.

        This is separated fom __call__ so that it can be decorated by calls to
        'for_groups' and 'for_state'.

        The Always True permission is used if no actual method is ever given, allowing
        for static or filtered only permissions.
        """
        return self.method(workflow_) if self.method else True

    def __call__(self, workflow_: 'workflow.Workflow') -> t.Union['Permission', bool, t.Callable]:
        """Decorate the workflow."""
        # _waiting_to_decorate is switched off on Workflow class creation,
        # at the metaclass
        if self._waiting_to_decorate:
            self.method = workflow_
            return self

        context = workflow_.context
        state = workflow_.state
        groups = self.groups
        states = self.states
        # Check Group Permission
        if groups and not (context and groups.intersection(context.groups)):
            return False

        # Check state
        if states:
            # This checking must be done here because WorkflowState's names are
            # lazily bound at the Workflow metaclass
            if isinstance(states, list):
                self.states = {s.value if hasattr(s, 'value') else s for s in states}
            if state.value not in states:
                return False

        if self.method:
            return self.method(workflow_)
        return True

    def for_groups(self, *args) -> 'Permission':
        """Apply permission just to some groups.

        Chain call that decorates this permission so that it is filtered restricting the
        permission to the groups passed in.
        """
        args = self._process_groups(args)
        self.groups.update(args)
        return self

    def for_states(self, *args) -> 'Permission':
        """Apply permission just for some states.

        Chain call that decorates this permission so that
        it is filtered restricting the permission to the states passed in.
        """
        # self.states can't be a set at this point because
        # states may be referenced by objects  - with late
        # name binding) - that are unhashable
        self.states.extend(args)
        return self

    def __get__(self, instance: t.Optional['workflow.Workflow'], owner: t.Any) -> 'Permission':
        """Get the permission."""
        if instance is None:
            return self
        return self(instance)
