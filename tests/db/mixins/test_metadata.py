"""Test BaseMetadata mixin."""
from briefy.common.db import Base
from briefy.common.db.mixins import BaseMetadata
from briefy.common.db.mixins import Mixin
from conftest import DBSession

import pytest


content_data = {
    'updated_at': '2016-09-08T15:36:28.087123Z',
    'title': 'Berlin',
    'description': 'Hauptstadt Deutsch',
    'slug': 'hauptstadt-deutsch',
    'id': '6b6f0b2a-25ed-401c-8c65-3d4009e398ea',
    'created_at': '2016-09-08T15:36:28.087112Z'
}


class Content(BaseMetadata, Mixin, Base):
    """A content containing title, description and a slug."""

    __tablename__ = 'contents'
    __session__ = DBSession


@pytest.mark.usefixtures('db_transaction')
class TestBaseMetadataMixin:
    """Test Base metadata mixin."""

    def test_mixin(self, session):
        """Test mixin."""
        content = Content(**content_data)
        session.add(content)
        session.commit()
        session.flush()
        content = session.query(Content).first()

        assert isinstance(content, Content)

        assert content.slug == content_data['slug']

        # Set an empty slug should fallback to generated slug
        content.slug = None
        expected = '{0}-{1}'.format(content_data['id'][:8], 'berlin')
        assert content.slug == expected

        session.commit()
        session.flush()

        # Search should work as well
        results = Content.query().filter(
            Content.slug == expected
        ).all()
        assert len(results) == 1
        assert results[0].slug == expected
