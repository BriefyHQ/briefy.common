"""Tests for `briefy.common.queue.event` module."""
from briefy.common.db import Base
from briefy.common.db.mixins import Mixin
from briefy.common.event import BaseEvent
from briefy.common.queue.message import SQSMessage
from briefy.common.users import SystemUser
from briefy.common.workflow import BriefyWorkflow
from briefy.common.workflow import WorkflowState
from conftest import BriefyQueueBaseTest
from conftest import DBSession
from datetime import date

import colander
import json
import pytest
import re
import sqlalchemy as sa


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
    __session__ = DBSession

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
def new_simple(request, session):
    x = SimpleModel()
    x.name = "foo"
    x.birthday = date.today()
    session.add(x)
    session.flush()
    return x


@pytest.mark.usefixtures("db_transaction")
class TestSQSMessage(BriefyQueueBaseTest):

    schema = SimpleSchema

    def test_model_is_created(self, new_simple, session):
        """Asserts a model creation, persistance, retrieval and representation

        :param new_simple: A Model object supplied by dependency injection
        :type new_simple: SimpleModel
        """
        x = new_simple
        y = session.query(SimpleModel).all()[0]
        z = SimpleModel.get(x.id)
        assert x.name == y.name == z.name
        assert x.birthday == y.birthday == z.birthday
        assert re.match(r"\<SimpleModel\(id='.+?' state='created' created='.+?' updated='.+?'\)\>", repr(y))  # noqa

    def test_init_with_valid_body(self):
        """Test message with a valid body."""
        body = {'event_name': 'job.created'}
        message = SQSMessage(self.schema, body=body)

        assert isinstance(message, SQSMessage)
        assert message.body == body

    def test_simple_created_is_put_on_sqs(self, new_simple, session):
        x = new_simple
        y = session.query(SimpleModel).all()[0]
        self._setup_queue()
        event = SimpleCreated(y, actor=str(SystemUser.id))
        event()
        message = self.get_from_queue()
        data = json.loads(message.body)['data']
        assert data['birthday'] == x.birthday.isoformat() + 'T00:00:00'
        assert data['name'] == x.name

    def test_model_raising_error_on_write(self, new_simple, session):
        self._setup_queue()
        event = SimpleCreated(new_simple, actor=str(SystemUser.id))
        # Will not have an event name
        event.event_name = ''
        event()
        messages = self.queue.receive_messages(MaxNumberOfMessages=10)
        assert len(messages) == 0

    def test_model_without_created_at(self, session):
        self._setup_queue()
        y = session.query(SimpleModel).all()[0]
        del(y.created_at)
        with pytest.raises(ValueError):
            SimpleCreated(y, actor=str(SystemUser.id))
