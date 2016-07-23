"""Tests for `briefy.common.queue.event` module."""

from briefy.common.db import Base
from briefy.common.db.mixins import Mixin
from briefy.common.event import BaseEvent
from briefy.common.queue.message import SQSMessage
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState
from conftest import BriefyQueueBaseTest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import colander
import json
import pytest
import re
import sqlalchemy as sa


def _create_testing_db():
    Session = sessionmaker()
    engine = create_engine('sqlite://')
    session = Session(bind=engine)
    Base.metadata.bind = engine
    return session


session = _create_testing_db()


# TODO: refactor workflow, model, etc definitions to other file.
class SimpleWorkflow(BriefyWorkflow):
    """Workflow for a Lead."""

    # Optional name for this workflow
    entity = 'simple'
    initial_state = 'created'

    created = WorkflowState('created', title='Created', description='Simple model created')


class SimpleModel(Mixin, Base):
    """A possible customer or professional that visited briefy.co website."""

    __tablename__ = 'simple'
    __session__ = session

    _workflow = SimpleWorkflow

    name = sa.Column(sa.String(255), nullable=False)
    birthday = sa.Column(sa.Date)


class SimpleSchema(colander.MappingSchema):
    """Payload for this queue."""

    event_name = colander.SchemaNode(
        colander.String(),
        validator=colander.Regex(r'^(([a-z])+\.([a-z])+)+$')
    )


class SimpleCreated(BaseEvent):
    """A Lead was created."""

    event_name = 'simple.created'


@pytest.fixture
def new_db():
    # global session
    Base.metadata.drop_all()
    Base.metadata.create_all()
    return session


@pytest.fixture
def new_simple():
    x = SimpleModel()
    x.name = "foo"
    x.birthday = date.today()
    return x


def test_model_is_created(new_simple, new_db):
    """Asserts a model creation, persistance, retrieval and representation

    :param new_simple: A Model object supplied by dependency injection
    :type new_simple: SimpleModel
    """
    x = new_simple
    new_db.add(x)
    new_db.commit()
    y = SimpleModel.query().all()[0]
    z = SimpleModel.get(x.id)
    assert x.name == y.name == z.name
    assert x.birthday == y.birthday == z.birthday
    assert re.match(r"\<SimpleModel\(id='.+?' state='created' created='.+?' updated='.+?'\)\>", repr(y))  # noqa


class TestSQSMessage(BriefyQueueBaseTest):

    schema = SimpleSchema

    def test_init_with_valid_body(self):
        """Test message with a valid body."""
        body = {'event_name': 'job.created'}
        message = SQSMessage(self.schema, body=body)

        assert isinstance(message, SQSMessage)
        assert message.body == body

    def test_simple_created_is_put_on_sqs(self, new_db, new_simple):
        x = new_simple
        new_db.add(x)
        new_db.commit()
        y = SimpleModel.query().all()[0]
        self._setup_queue()
        event = SimpleCreated(y)
        event()
        message = self.get_from_queue()
        data = json.loads(message.body)['data']
        assert data['birthday'] == x.birthday.isoformat() + 'T00:00:00'
        assert data['name'] == x.name
