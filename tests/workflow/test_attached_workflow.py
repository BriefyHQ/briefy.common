from briefy import common
from briefy.common.db import Base
from briefy.common.db.mixins import Mixin
from briefy.common.db.mixins.workflow import WorkflowBase
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState
from briefy.common.workflow import WorkflowStateGroup
from briefy.common.workflow.exceptions import WorkflowStateException
from briefy.common.workflow.exceptions import WorkflowTransitionException
from conftest import queue_url
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from zope.configuration.xmlconfig import XMLConfig

import botocore
import pytest


class Content(WorkflowBase):
    """A base content."""

    id = '123'
    created_at = datetime.now()
    updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Return a dictionary with fields and values used by this Class.

        :returns: Dictionary with fields and values used by this Class
        """
        data = self.__dict__.copy()
        data['state_history'] = self.state_history
        return data


@pytest.fixture
def mock_sqs():
    class MockEndpoint(botocore.endpoint.Endpoint):
        def __init__(self, host, *args, **kwargs):
            super().__init__(queue_url(), *args, **kwargs)

    botocore.endpoint.Endpoint = MockEndpoint

    XMLConfig('configure.zcml', common)()


@pytest.fixture
def session():
    Session = sessionmaker()
    engine = create_engine('postgresql://briefy:briefy@127.0.0.1:9999/briefy-common')
    session = Session(bind=engine)
    Base.metadata.bind = engine
    return session


@pytest.fixture
def simple_workflow():
    class SimpleWorkflow(BriefyWorkflow):
        entity = 'test'
        initial_state = 's1'
        s1 = WorkflowState("s1", title="1", description="first")
        s2 = WorkflowState("s2", title="2", description="second")
    return SimpleWorkflow


# Used as guard to ensure the model is created just once in a test session
SimpleModel = None
MediumModel = None


@pytest.fixture
def simple_model(session, simple_workflow):
    global SimpleModel
    if not SimpleModel:
        class SimpleModel(Mixin, Base):
            __tablename__ = 'simple_model'
            __session__ = session
            _workflow = simple_workflow
    return SimpleModel


@pytest.fixture
def medium_workflow():
    class MediumWorkflow(BriefyWorkflow):
        entity = 'test'
        initial_state = 's1'
        s1 = WorkflowState("s1", title="1", description="first")
        s2 = WorkflowState("s2", title="2", description="second")

        def permissions(self):
            return ['just_do_it']

        @s1.transition(state_to=s2, permission='just_do_it')
        @s2.transition(state_to=s1, permission='just_do_it')
        def flip(self):
            """ Simply flips state """
            pass

    return MediumWorkflow


@pytest.fixture
def medium_model(session, medium_workflow):
    global MediumModel
    if not MediumModel:
        class MediumModel(Mixin, Base):
            __tablename__ = 'medium_model'
            __session__ = session
            _workflow = medium_workflow
    return MediumModel


@pytest.fixture
def persisted_object(simple_model, medium_model):
    Base.metadata.create_all()
    session = simple_model.__session__
    a = simple_model()
    session.rollback()
    session.add(a)
    session.flush()
    return a


def test_workflow_exists_in_model(persisted_object, mock_sqs):
    assert persisted_object.workflow
    assert persisted_object.workflow.name == 'test.workflow'


def test_workflow_initial_state_works(persisted_object, mock_sqs):
    # Previous behavior had a 'created' default value hardcoded
    # in the sqlalchemy declaration of the 'state' field.
    # No other initial state would work

    # This also asserts that the initial state is set upon
    # object instantiation. (Previous behavior worked due to
    # said default value)
    assert persisted_object.state == 's1'
    assert persisted_object.workflow.state.name == 's1'


def test_workflow_state_can_be_called(persisted_object, mock_sqs):
    assert persisted_object.workflow.s1()
    assert not persisted_object.workflow.s2()


def test_workflow_unattached_state_cant_be_checked(simple_workflow, mock_sqs):
    with pytest.raises(WorkflowStateException):
        simple_workflow.s1()


def test_workflow_states_property(persisted_object, mock_sqs):
    wf = persisted_object.workflow
    assert wf.states
    assert len(wf.states) == 2
    assert wf.states.s1
    assert wf.states['s1']
    assert wf.states['s2'] is wf.states.s2
    assert wf.states.s1 != wf.states.s2
    assert 'SimpleWorkflow' in repr(wf.states)
    with pytest.raises(AttributeError):
        wf.states.s3


def test_workflow_states_can_flip(medium_workflow, mock_sqs):
    class M(Content):
        _workflow = medium_workflow

    obj = M()
    assert obj.state == 's1'
    obj.workflow.flip()
    assert obj.state == 's2'
    obj.workflow.flip()
    assert obj.state == 's1'


def test_workflow_transition_with_incorrect_name_fails(mock_sqs):
    class MediumWorkflow(BriefyWorkflow):
        entity = 'test'
        initial_state = 's1'
        s1 = WorkflowState("s1", title="1", description="first")
        s2 = WorkflowState("s2", title="2", description="second")

        def permissions(self):
            return ['just_do_it']

        @s1.transition(state_to=s2, permission='just_do_it')
        def flip(self):
            """ Simply flips state """
            pass

    class M(Content):
        _workflow = MediumWorkflow

    obj = M()
    with pytest.raises(WorkflowTransitionException):
        obj.workflow.flip()
        obj.workflow.flip()


def test_workflow_transition_passes_without_permission(medium_workflow, mock_sqs):
    medium_workflow.permissions = lambda self: ['another_fake_permission']

    class M(Content):
        _workflow = medium_workflow

    obj = M()
    obj.workflow.flip()


def test_workflow_transition_from(mock_sqs):
    class MediumWorkflow(BriefyWorkflow):
        entity = 'test'
        initial_state = 's1'
        s1 = WorkflowState("s1", title="1", description="first")
        s2 = WorkflowState("s2", title="2", description="second")

        def permissions(self):
            return ['just_do_it']

        @s2.transition_from(s1, permission='just_do_it')
        def flip(self):
            """ Simply flips state """
            pass

    class M(Content):
        _workflow = MediumWorkflow

    obj = M()
    assert obj.state == 's1'
    obj.workflow.flip()
    assert obj.state == 's2'


def test_workflow_state_group(medium_workflow, mock_sqs):
    """
    Several unitary tests for WorkflowStategroup:

    Assert WorkflowStategroups can't be detachhed

    Assert WorkflowStategroups are callable, and return True if the object is in
    a state in the group. False if current state is not in the group

    Assert WorkflowStategroups membership operator ("in") operator works
    for states passed both as objects and by name

    Asserts transitions can't be declared for WorkflowStategroups

    """
    group_s = WorkflowStateGroup([medium_workflow.s1, medium_workflow.s2])

    with pytest.raises(WorkflowStateException):
        group_s()

    class DerivedWorkflow(medium_workflow):
        group_s = WorkflowStateGroup([medium_workflow.s1])

    class M(Content):
        _workflow = DerivedWorkflow

    obj = M()

    assert obj.workflow.group_s()
    obj.workflow.flip()
    # assert not obj.workflow.group_s()
    assert obj.workflow.s1 in obj.workflow.group_s
    assert 's1' in obj.workflow.group_s

    assert 'WorkflowStateGroup' in repr(obj.workflow.group_s)

    with pytest.raises(TypeError):
        class DerivedWorkflow(medium_workflow):
            group_s = WorkflowStateGroup([medium_workflow.s1, medium_workflow.s2])

            @group_s.transition(medium_workflow.s2)
            def flip(self):
                pass


def test_workflow_raises_on_unknown_state(simple_workflow, mock_sqs):
    class M(Content):
        _workflow = simple_workflow
        state = 'unknown'

    with pytest.raises(WorkflowStateException):
        M()


def test_workflow_representation(simple_workflow, mock_sqs):
    class M(Content):
        _workflow = simple_workflow
    assert 'Workflow' in repr(M().workflow)


def test_workflow_works_for_a_dictionary(simple_workflow, mock_sqs):
    obj = {'state': None, 'state_history': None}
    simple_workflow(obj)
    assert obj['state'] == 's1'


def test_workflow_notifications(medium_workflow, mock_sqs):
    class OtherWorkflow(medium_workflow):
        def _notify(self, transition):
            self.document.test_transitioned = True
            super()._notify(transition)

    class M(Content):
        _workflow = OtherWorkflow

    obj = M()
    obj.workflow.flip()
    assert obj.state == 's2'
    assert obj.test_transitioned
