"""Document briefy.common.workflows.BriefyWorkflow."""
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from graphviz import Digraph
from importlib import import_module
from sphinx.ext.graphviz import html_visit_graphviz
from sphinx.util.compat import Directive
from sphinx.util.docstrings import prepare_docstring

import docutils


class workflow_diagram(nodes.General, nodes.Inline, nodes.Element):
    """A node containing a Workflow Diagram."""

    pass


def generate_graph(workflow) -> str:
    """Generate the Graphviz workflow.

    :param workflow: Workflow to be documented.
    :return: Graphviz dot source for the Workflow.
    """
    def fmt_label(title: str, caption: str, title_size: int=12, caption_size: int=8) -> str:
        """Return a label with two lines."""
        return (
            '<<FONT POINT-SIZE="{title_size}">{title}</FONT><BR />'
            '<FONT POINT-SIZE="{caption_size}">{caption}</FONT>>'
        ).format(title=title, caption=caption, title_size=title_size, caption_size=caption_size,)

    dot = Digraph()
    title = fmt_label(workflow.__name__, workflow.__doc__, 20, 14)
    dot.body.extend(
        ['labelloc="t"', 'rankdir=TD', 'fontsize=20', 'label={label}'.format(label=title),]
    )
    states = workflow._states_sorted
    initial = workflow.initial_state
    transitions = []

    # Start node
    dot.attr('node', shape='point', style='filled', fillcolor='#000000')
    dot.node('initial')

    dot.attr('node', shape='box', height='0.6', width='1.6', style='',fixedsize='true')

    for state in states:
        id_ = state.name
        title = state.title
        label = fmt_label(title, id_, 12, 10)
        dot.node(state.name,label=label,)
        transitions.extend([v for k, v in state._transitions.items()])

    dot.edge('initial', initial)
    for t in transitions:
        from_ = t.state_from().name
        to_ = t.state_to().name
        title = t.title
        label = fmt_label(title, t.name, 10, 8)
        dot.edge(from_, to_, label=label,)

    return dot.source


class WorkflowDirective(Directive):
    """ Workflow directive.

    Injects sections in the documentation about the Workflow.
    """
    has_content = True
    option_spec = {
        'class': directives.unchanged,
    }
    domain = 'briefy'
    doc_field_types = []

    def __init__(self, *args, **kwargs):
        """Initialize this Directive."""
        super(WorkflowDirective, self).__init__(*args, **kwargs)
        self.env = self.state.document.settings.env
        pieces = self.options.get('class').split('.')
        module = '.'.join(pieces[:-1])
        klassname = pieces[-1]
        self.wf = getattr(import_module(module),klassname)
        self.wf_name = self.wf._name
        self.wf_elements = self._workflow_elements()

    def _rst2node(self, body: str) -> docutils.nodes.paragraph:
        """Process an ReSTructuredTect block and return a paragraph containing it.

        Used, primarily, to process docstrings.
        """
        node = nodes.paragraph()
        result = ViewList(prepare_docstring(body))
        self.state.nested_parse(result, 0, node)
        return node

    def _workflow_elements(self) -> dict:
        """Return a dictionary with states, transitions and permissions."""
        states = []
        transitions = []
        permissions = []
        wf = self.wf
        for state in wf._states_sorted:
            states.append(state)
            transitions.extend([v for k, v in state._transitions.items()])
        for p_name in wf._existing_permissions:
            permission = wf._existing_permissions[p_name]
            permissions.append(permission)
        return {
            'states': states,
            'transitions': transitions,
            'permissions': permissions,
        }

    def document_states(self) -> docutils.nodes.section:
        """Document workflow states.

        :returns: A section node containing the doctree for states description.
        """
        states = self.wf_elements.get('states')
        wf_name = self.wf_name
        node = nodes.section(ids=[
            'workflows-{wf_name}-states'.format(wf_name=wf_name)
        ])
        node += nodes.title(text='States')
        dl = nodes.definition_list()
        for state in states:
            state_id = 'workflows-{wf_name}-states-{state}'.format(
                wf_name=wf_name,
                state=state.name
            )
            state_node = nodes.definition_list_item()
            state_node += nodes.term(text=state.title, ids=[state_id])
            dd = nodes.definition()
            dd += self._rst2node(state.description)
            transitions = nodes.bullet_list()
            for t_name in state._transitions:
                t = state._transitions[t_name]
                temp = nodes.list_item()
                temp += nodes.inline(text=t.name)
                temp += nodes.inline(
                    text=' ({state_to})'.format(state_to=t.state_to().name)
                )
                transitions += temp
            dd += transitions
            state_node += dd
            dl += state_node
        node += dl
        return node

    def document_transitions(self) -> docutils.nodes.section:
        """Document workflow transitions.

        :returns: A section node containing the doctree for transitions description.
        """
        transitions = self.wf_elements.get('transitions')
        wf_name = self.wf_name
        node = nodes.section(ids=[
            'workflows-{wf_name}-transitions'.format(wf_name=wf_name)
        ])
        node += nodes.title(text='Transitions')
        dl = nodes.definition_list()
        for transition in transitions:
            transition_id = 'workflows-{wf_name}-transitions-{transition}'.format(
                wf_name=wf_name,
                transition=transition.name
            )
            t_node = nodes.definition_list_item()
            title = '{title} ({from_} → {to_})'.format(
                title=transition.title,
                from_=transition.state_from().name,
                to_=transition.state_to().name,
            )
            t_node += nodes.term(text=title, ids=[transition_id])
            dd = nodes.definition()
            dd += self._rst2node(transition.__doc__)
            dd += nodes.paragraph(
                text='Permission: {permission}'.format(permission=transition.permission)
            )
            t_node += dd
            dl += t_node
        node += dl
        return node

    def document_permissions(self) -> docutils.nodes.section:
        """Document workflow permissions.

        :returns: A section node containing the doctree for permissions description.
        """
        permissions = self.wf_elements.get('permissions')
        wf_name = self.wf_name
        node = nodes.section(ids=[
            'workflows-{wf_name}-permissions'.format(wf_name=wf_name)
        ])
        node += nodes.title(text='Permissions')
        dl = nodes.definition_list()
        for permission in permissions:
            permission_id = 'workflows-{wf_name}-permissions-{permission}'.format(
                wf_name=wf_name,
                permission=permission.name
            )
            t_node = nodes.definition_list_item()
            t_node += nodes.term(text=permission.name, ids=[permission_id])
            dd = nodes.definition()
            dd += self._rst2node(permission.__doc__)
            if hasattr(permission, 'groups'):
                dd += nodes.paragraph(
                    text='Groups: {groups}'.format(
                        groups=', '.join(permission.groups)
                    )
                )
            t_node += dd
            dl += t_node
        node += dl
        return node

    def graph_workflow(self) -> nodes.section:
        """Generate a graphical representation of this Workflow."""
        source = generate_graph(self.wf)
        wf_name = self.wf_name
        node = nodes.section(ids=[
            'workflows-{wf_name}-diagram'.format(wf_name=wf_name)
        ])
        node += nodes.title(text='Diagram')
        node_diagram = workflow_diagram()
        node_diagram['code'] = source
        node_diagram['options'] = {}
        node += node_diagram
        return node

    def run(self) -> list:
        """Process the directive.

        :returns: List of nodes.
        """
        states = self.document_states()
        transitions = self.document_transitions()
        permissions = self.document_permissions()
        graph = self.graph_workflow()
        return [states, transitions, permissions, graph ]


def setup(app):
    """Setup the extension."""
    app.add_node(workflow_diagram, html=(html_visit_graphviz, None))
    app.add_directive('workflow', WorkflowDirective)
    return {
        'version': '1.0'
    }
