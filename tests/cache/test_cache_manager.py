"""Test CacheManager utility."""
from briefy.common.db.mixins import SubItemMixin
from briefy.common.db.models import Item
from conftest import DBSession
from dogpile.cache.backends.memory import MemoryBackend
from dogpile.cache.backends.redis import RedisBackend

import pytest
import uuid


dummy_cache_data = {
    'title': 'Dummy Cache Item',
    'updated_at': '2016-09-08T15:36:28.087123Z',
    'id': '6b6f0b2a-25ed-401c-8c65-3d4009e398ea',
    'path': [uuid.UUID('6b6f0b2a-25ed-401c-8c65-3d4009e398ea')],
    'created_at': '2016-09-08T15:36:28.087112Z',
    'state': 'created',
}

CACHE_BACKENDS = {
    'dogpile.cache.memory': MemoryBackend,
    'dogpile.cache.redis': RedisBackend
}


class DummyCache(SubItemMixin, Item):
    """A content containing title, description and a slug."""

    __tablename__ = 'dummycaches'
    __session__ = DBSession

    def to_dict(self, excludes: list = None, includes: list = None) -> dict:
        """Return a dict version to serialize the object."""
        return super().to_dict(excludes, includes)


@pytest.fixture
def dummy_cache_obj(session):
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
    @pytest.mark.parametrize('backend', ['dogpile.cache.memory', 'dogpile.cache.redis'])
    def test_cache_backends_refresh(self, cache_manager, dummy_cache_obj):
        """Test cache manager memory backend configuration."""
        backend_klass = CACHE_BACKENDS.get(cache_manager._backend)
        cache_manager._create_region()
        region = cache_manager.region()
        assert isinstance(region.backend, backend_klass) is True

        content = dummy_cache_obj
        data = content.to_dict()
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
