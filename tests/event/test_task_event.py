"""Tests for `briefy.common.queue.event` module."""
from briefy.common.db import Base
from briefy.common.db.mixins import Mixin
from briefy.common.event import TaskEvent
from conftest import BriefyQueueBaseTest
from conftest import DBSession

import colander
import json
import pytest
import sqlalchemy as sa


class DummyModel(Mixin, Base):
    """A possible customer or professional that visited briefy.co website."""

    __tablename__ = 'dummt'
    __session__ = DBSession

    title = sa.Column(sa.String(255), nullable=False)


class SimpleSchema(colander.MappingSchema):
    """Payload for this queue."""

    event_name = colander.SchemaNode(
        colander.String(),
        validator=colander.Regex(r'^(([a-z])+\.([a-z])+)+$')
    )


class InternalTask(TaskEvent):
    """An internal task event."""


@pytest.fixture
def new_dummy(request, session):
    x = DummyModel()
    x.title = 'An Object'
    session.add(x)
    session.flush()
    return x


@pytest.mark.usefixtures("db_transaction")
class TestTaskEvent(BriefyQueueBaseTest):

    schema = SimpleSchema

    def test_task_event_with_object_and_data(self, new_dummy, session):
        self._setup_queue()
        task_name = 'briefy.internal.tick'
        success = True
        x = new_dummy
        obj = session.query(DummyModel).all()[0]
        data = obj.to_dict()
        event = InternalTask(task_name=task_name, success=success, obj=obj, data=data)
        event()
        message = self.get_from_queue()
        body = json.loads(message.body)
        assert body['event_name'] == 'briefy.internal.tick.success'
        assert body['data']['title'] == x.title

    def test_task_event_with_object(self, new_dummy, session):
        self._setup_queue()
        task_name = 'briefy.internal.tick'
        success = True
        x = new_dummy
        obj = session.query(DummyModel).all()[0]

        event = InternalTask(task_name=task_name, success=success, obj=obj)
        event()
        message = self.get_from_queue()
        body = json.loads(message.body)
        data = body['data']
        assert body['event_name'] == 'briefy.internal.tick.success'
        assert data['title'] == x.title

        success = False
        event = InternalTask(task_name=task_name, success=success, obj=obj)
        event()
        message = self.get_from_queue()
        body = json.loads(message.body)
        data = body['data']
        assert body['event_name'] == 'briefy.internal.tick.failure'
        assert data['title'] == x.title

    def test_task_event_with_data(self):
        self._setup_queue()
        task_name = 'briefy.internal.cron'
        success = True
        payload = {
            'id': '9b04473d-ecca-4422-83ed-f4f9635ad59c',
            'foo': 'bar'
        }

        event = InternalTask(task_name=task_name, success=success, data=payload)
        event()
        message = self.get_from_queue()
        body = json.loads(message.body)
        data = body['data']
        assert body['event_name'] == 'briefy.internal.cron.success'
        assert data['foo'] == 'bar'

        success = False
        event = InternalTask(task_name=task_name, success=success, data=payload)
        event()
        message = self.get_from_queue()
        body = json.loads(message.body)
        assert body['event_name'] == 'briefy.internal.cron.failure'

    def test_task_event_without_data_or_obj(self):
        self._setup_queue()
        task_name = 'briefy.internal.cron'
        success = True
        with pytest.raises(ValueError):
            InternalTask(task_name=task_name, success=success, data=None, obj=None)
