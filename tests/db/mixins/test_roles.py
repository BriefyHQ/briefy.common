"""Test BriefyRoles mixin."""
from briefy.common.db import Base
from briefy.common.db.mixins import BriefyRoles
from briefy.common.db.mixins import Mixin
from conftest import DBSession

import pytest


job_data = {
    'updated_at': '2016-09-08T15:36:28.087123Z',
    'project_manager': 'e9bee447-91ea-468f-b247-1ba4b9cf79ac',
    'finance_manager': 'df114979-f0fa-423e-8761-0f57672153dd',
    'qa_manager': '92a40b92-8c04-407d-9922-097ba5171e2d',
    'scout_manager': 'edb4d4be-8b22-4818-894e-3da6317087f4',
    'id': '6b6f0b2a-25ed-401c-8c65-3d4009e398ea',
    'created_at': '2016-09-08T15:36:28.087112Z'
}


class DummyJob(BriefyRoles, Mixin, Base):
    """A content containing title, description and a slug."""

    __tablename__ = 'dummy_jobs'
    __session__ = DBSession


@pytest.mark.usefixtures("db_transaction")
class TestBriefyRolesMixin:
    """Test BriefyRoles mixin."""

    def test_mixin(self, session):
        """Test mixin."""
        job = DummyJob(**job_data)
        session.add(job)
        session.commit()
        session.flush()
        job = session.query(DummyJob).first()

        assert isinstance(job, DummyJob)

        assert str(job.project_manager) == 'e9bee447-91ea-468f-b247-1ba4b9cf79ac'
        assert str(job.finance_manager) == 'df114979-f0fa-423e-8761-0f57672153dd'
        assert str(job.qa_manager) == '92a40b92-8c04-407d-9922-097ba5171e2d'
        assert str(job.scout_manager) == 'edb4d4be-8b22-4818-894e-3da6317087f4'

        job.project_manager = 'c087fa7e-738b-412a-80c7-a139ab9c373d'
        assert str(job.project_manager) == 'c087fa7e-738b-412a-80c7-a139ab9c373d'
