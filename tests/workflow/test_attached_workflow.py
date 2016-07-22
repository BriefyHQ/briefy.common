from briefy.common.db import Base
from briefy.common.db.mixins import Mixin
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState
from briefy.common.workflow.exceptions import WorkflowStateException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pytest


@pytest.fixture
def session():
    Session = sessionmaker()
    engine = create_engine('sqlite://')
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

SimpleModel = None


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
def persisted_object(simple_model):
    Base.metadata.create_all()
    session = simple_model.__session__
    a = simple_model()
    session.rollback()
    session.add(a)
    session.flush()
    return a


def test_workflow_exists_in_model(persisted_object):
    assert persisted_object.workflow
    assert persisted_object.workflow.name == 'test.workflow'


def test_workflow_initial_state_works(persisted_object):
    # Previous behavior had a 'created' default value hardcoded
    # in the sqlalchemy declaration of the 'state' field.
    # No other initial state would work

    # This also asserts that the initial state is set upon
    # object instantiation. (Previous behavior worked due to
    # said default value)
    assert persisted_object.state == 's1'
    assert persisted_object.workflow.state.name == 's1'


def test_workflow_state_can_be_called(persisted_object):
    assert persisted_object.workflow.s1()
    assert not persisted_object.workflow.s2()


def test_workflow_unattached_state_cant_be_checked(simple_workflow):
    with pytest.raises(WorkflowStateException):
        simple_workflow.s1()

def test_workflow_states_property(persisted_object):
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
