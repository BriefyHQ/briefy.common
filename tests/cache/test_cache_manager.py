"""Test CacheManager utility."""
from briefy.common.db import Base
from briefy.common.db.mixins import BriefyRoles
from briefy.common.db.mixins import Mixin
from conftest import DBSession

import pytest


dummy_cache_data = {
    'updated_at': '2016-09-08T15:36:28.087123Z',
    'project_manager': 'e9bee447-91ea-468f-b247-1ba4b9cf79ac',
    'qa_manager': '92a40b92-8c04-407d-9922-097ba5171e2d',
    'scout_manager': 'edb4d4be-8b22-4818-894e-3da6317087f4',
    'id': '6b6f0b2a-25ed-401c-8c65-3d4009e398ea',
    'created_at': '2016-09-08T15:36:28.087112Z',
    'state': 'created',
}


class DummyCache(BriefyRoles, Mixin, Base):
    """A content containing title, description and a slug."""

    __tablename__ = 'dummy_cache'
    __session__ = DBSession
    __table_args__ = {'extend_existing': True}

    def to_dict(self, excludes: list = None, includes: list = None) -> dict:
        """Return a dict version to serialize the object."""
        return super().to_dict(excludes, includes)


@pytest.fixture
def dummy_cache_obj(cache_manager, session):
    """Create a new DummyCache content."""
    uid = dummy_cache_data.get('id')
    content = DummyCache.get(uid)
    if not content:
        content = DummyCache(**dummy_cache_data)
        session.add(content)
        session.commit()
        session.flush()
        content = session.query(DummyCache).first()
    return content


@pytest.mark.usefixtures('db_transaction')
class TestCacheManager:
    """Test CacheManager."""

    @pytest.mark.parametrize('enable_refresh', [True, False])
    @pytest.mark.parametrize('backend', ['dogpile.cache.memory'])
    def test_config_backend_memory(self, cache_manager, dummy_cache_obj):
        """Test cache manager memory backend configuration."""
        assert cache_manager._backend == 'dogpile.cache.memory'
        content = dummy_cache_obj
        data = content.to_dict()
        region = cache_manager.region()
        generator = cache_manager.key_generator('', content.to_dict)
        key = generator(content)
        region.set(key, data)
        cached_data = region.get(key)
        assert cached_data == data
        assert data.get('state') == dummy_cache_data.get('state')
        cache_manager.refresh(content)

        new_state = 'new_state'
        content.state = new_state
        data = content.to_dict()
        assert data.get('state') != dummy_cache_data.get('state')
        assert data.get('state') == new_state
        content.state = 'created'
        cache_manager.refresh(content)

    @pytest.mark.parametrize('enable_refresh', [True, False])
    @pytest.mark.parametrize('backend', ['dogpile.cache.redis'])
    def test_config_backend_redis(self, cache_manager, dummy_cache_obj):
        """Test cache manager redis backend configuration."""
        assert cache_manager._backend == 'dogpile.cache.redis'
        content = dummy_cache_obj
        data = content.to_dict()

        region = cache_manager.region()
        generator = cache_manager.key_generator('', content.to_dict)
        key = generator(content)
        region.set(key, data)
        cached_data = region.get(key)
        assert cached_data == data
        assert data.get('state') == dummy_cache_data.get('state')
        cache_manager.refresh(content)

        new_state = 'new_state'
        content.state = new_state
        data = content.to_dict()
        assert data.get('state') != dummy_cache_data.get('state')
        assert data.get('state') == new_state
        content.state = 'created'
        cache_manager.refresh(content)
