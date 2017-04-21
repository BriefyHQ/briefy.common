"""Test BriefyRoles mixin."""
from briefy.common.db import Base
from briefy.common.db.mixins import BriefyRoles
from briefy.common.db.mixins import Mixin
from briefy.common.types import BaseUser
from briefy.common.vocabularies.roles import LocalRolesChoices
from conftest import DBSession

import pytest


job_data = {
    'updated_at': '2016-09-08T15:36:28.087123Z',
    'project_manager': 'e9bee447-91ea-468f-b247-1ba4b9cf79ac',
    'qa_manager': '92a40b92-8c04-407d-9922-097ba5171e2d',
    'scout_manager': 'edb4d4be-8b22-4818-894e-3da6317087f4',
    'id': '6b6f0b2a-25ed-401c-8c65-3d4009e398ea',
    'created_at': '2016-09-08T15:36:28.087112Z'
}


class DummyJob(BriefyRoles, Mixin, Base):
    """A content containing title, description and a slug."""

    __tablename__ = 'dummy_jobs'
    __session__ = DBSession


@pytest.mark.usefixtures('db_transaction')
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

        def user_ids(role):
            """Return a list of user_ids on a given role."""
            return [str(lr.user_id) for lr in role]

        assert 'e9bee447-91ea-468f-b247-1ba4b9cf79ac' in user_ids(job.project_manager)
        assert '92a40b92-8c04-407d-9922-097ba5171e2d' in user_ids(job.qa_manager)
        assert 'edb4d4be-8b22-4818-894e-3da6317087f4' in user_ids(job.scout_manager)

        job.project_manager = 'c087fa7e-738b-412a-80c7-a139ab9c373d'

        session.commit()
        session.flush()
        job = session.query(DummyJob).first()

        assert 'c087fa7e-738b-412a-80c7-a139ab9c373d' in user_ids(job.project_manager)
        assert len(user_ids(job.project_manager)) == 2

        user = BaseUser('c087fa7e-738b-412a-80c7-a139ab9c373d', {})

        assert len(job.get_user_roles(user)) == 1

        lr = job.get_local_role_for_user('project_manager', user)
        assert (lr.role_name == LocalRolesChoices.project_manager)

        job.remove_local_role(user, 'project_manager')
        session.commit()
        session.flush()
        job = session.query(DummyJob).first()

        assert 'c087fa7e-738b-412a-80c7-a139ab9c373d' not in user_ids(job.project_manager)
        assert len(user_ids(job.project_manager)) == 1

        roles = job.local_roles
        assert str(roles[0]).startswith('<LocalRole')
        assert 'e9bee447-91ea-468f-b247-1ba4b9cf79ac' in job._actors_ids()
        assert 'e9bee447-91ea-468f-b247-1ba4b9cf79ac' == job._actors_info()['project_manager'][0]
