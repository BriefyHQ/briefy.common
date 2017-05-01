"""Utility and helper functions to manage cached data."""
from briefy.common.log import logger
from dogpile.cache import make_region
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Attribute


class ICacheManager(Interface):
    """Utility that manages the cache for model objects."""

    _config = Attribute('Cache region configuration dict.')
    _backend = Attribute('Cache backend.')
    _region = Attribute('Cache region instance.')

    def refresh(obj):
        """Invalidate and refresh a given model object.."""

    def region():
        """Get the existing cache region."""

    def key_generator(namespace, fn, **kw):
        """Generate keys for all models objects."""


def handle_workflow_transition(event):
    """Handle workflow transition event."""
    manager = getUtility(ICacheManager)
    obj = event.obj
    manager.refresh(obj)


@implementer(ICacheManager)
class BaseCacheManager:
    """Base implementation of a cache manager Utility."""

    _config = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'redis_expiration_time': 60*60*1,   # 1 hours
        'distributed_lock': True
    }
    _backend = 'dogpile.cache.redis'
    _region = None

    def __init__(self):
        """Initialize the cache manager."""
        self._create_region()

    def refresh(self, obj):
        """Invalidate and refresh a given model object.."""
        region = self.region()
        region.invalidate(obj)
        klass = obj.__class__
        klass_name = klass.__name__
        uid = obj.id
        logger.info('Invalidate model {name} : {uid}'.format(
            name=klass_name,
            uid=uid
        ))

    def _create_region(self):
        """Create a new region instance."""
        backend = self._backend
        config = self._config
        region = make_region(
            function_key_generator=self.key_generator
        ).configure(
            backend,
            expiration_time=3600,
            arguments=config
        )
        self._region = region

    def region(self):
        """Get the existing cache region."""
        if not self._region:
            self._create_region()
        return self._region

    def key_generator(self, namespace, fn, **kw):
        """Generate keys for all models objects."""
        namespace = namespace or ''
        namespace = '{fname}{namespace}'.format(
            fname=fn.__name__,
            namespace=namespace,
        )

        def generate_key(*args):
            """Create unique key for each model using UID."""
            obj = args[0]
            name = obj.__class__.__name__
            key = '{name}.{namespace}-{id}'.format(
                name=name,
                namespace=namespace,
                id=obj.id,
            )
            return key

        return generate_key


def get_cache_manager():
    """Create a new CacheManager instance."""
    return BaseCacheManager()
