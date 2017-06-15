"""Test Workflow mix."""
from briefy.common.db import Base
from briefy.common.db.mixins import Identifiable
from briefy.common.db.mixins import Workflow
from conftest import DBSession

import pytest


class WorkflowExample(Workflow, Identifiable, Base):
    """A Workflow example."""

    __tablename__ = 'wf_examples'
    __session__ = DBSession


@pytest.mark.usefixtures('db_transaction')
class TestWorkflow:
    """Test Workflow database model."""

    def test_mixin(self, session):
        """Test mixin behavior."""
        example_data = {
            'id': '6b6f0b2a-25ed-401c-8c65-3d4009e398ea',
            'state': 'created',
            'state_history': [
                {
                    'message': 'Created by Briefy on Old database',
                    'from': '',
                    'date': '2017-01-30T15:25:00+00:00',
                    'to': 'created',
                    'actor': 'be319e15-d256-4587-a871-c3476affa309',
                    'transition': ''
                },
            ]
        }
        example = WorkflowExample(**example_data)
        session.add(example)
        session.commit()
        session.flush()
        example = session.query(WorkflowExample).first()

        assert isinstance(example, WorkflowExample)
        assert 'state_history' not in example.to_dict()
        assert 'state_history' in example.to_dict(includes=['state_history'])
