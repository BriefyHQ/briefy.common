"""Utility and helper functions to manage cached data."""
from briefy.common import config
from briefy.common.log import logger
from dogpile.cache import make_region
from threading import Thread
from zope.component import getUtility
from zope.interface import Attribute
from zope.interface import implementer
from zope.interface import Interface


BACKENDS_CONFIG = {
    'dogpile.cache.redis': {
        'arguments': {
            'host': config.CACHE_HOST,
            'port': config.CACHE_PORT,
            'db': 0,
            'redis_expiration_time': config.CACHE_EXPIRATION_TIME,
            'distributed_lock': True
        },
    },
    'dogpile.cache.pylibmc': {
        'arguments': {
            'url': ['{0}:{1}'.format(config.CACHE_HOST, config.CACHE_PORT)],
            'binary': True,
            'behaviors': {'tcp_nodelay': True, 'ketama': True}
        },
        'expiration_time': config.CACHE_EXPIRATION_TIME
    },
    'dogpile.cache.memory': {
        'expiration_time': config.CACHE_EXPIRATION_TIME
    }
}


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


def refresher(obj, *args, **kwargs):
    """Refresh model object cache."""
    logger.info('Starting async refresh for model {name} : {uid}'.format(
        **kwargs
    ))
    obj.to_dict()
    obj.to_listing_dict()
    obj.to_summary_dict()
    logger.info('Finishing async refresh for model {name} : {uid}'.format(
        **kwargs
    ))


@implementer(ICacheManager)
class BaseCacheManager:
    """Base implementation of a cache manager Utility."""

    _backend = config.CACHE_BACKEND
    _config = None
    _enable_refresh = False
    _region = None

    def __init__(self, backend=_backend):
        """Initialize the cache manager."""
        self._backend = backend
        self._enable_refresh = config.CACHE_ASYNC_REFRESH

    def refresh(self, obj):
        """Invalidate and refresh a given model object."""
        region = self.region()
        region.invalidate(obj)
        klass = obj.__class__
        klass_name = klass.__name__
        uid = obj.id
        log_kwargs = {
            'name': klass_name,
            'uid': uid
        }
        logger.info('Invalidate model {name} : {uid}'.format(
            **log_kwargs
        ))
        if self._enable_refresh:
            thread = Thread(target=refresher, args=[obj], kwargs=log_kwargs)
            thread.start()

    def _create_region(self):
        """Create a new region instance."""
        backend = self._backend
        config = self._config = BACKENDS_CONFIG.get(backend)
        region = make_region(
            function_key_generator=self.key_generator
        ).configure(
            backend,
            **config
        )
        logger.info('New dogpile.cache region created')
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

        def generate_key(*args, **kwargs):
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
