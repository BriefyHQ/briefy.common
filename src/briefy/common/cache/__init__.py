"""Utility and helper functions to manage cached data."""
from dogpile.cache import make_region
from multiprocessing import Process
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import object_session
from zope.component import getUtility
from zope.interface import implements
from zope.interface import Interface


class ICacheManager(Interface):
    """Utility that manages the cache for model objects."""

    _config = None
    _region = None

    def refresh(obj):
        """Invalidate and refresh a given model object.."""

    def region(config):
        """Get the existing cache region."""

    def key_generator(namespace, fn, **kw):
        """Generate keys for all models objects."""


def refresher(obj, **kwargs):
    """Function to refresh one model object."""
    obj.to_dict()
    obj.to_sumary_dict()
    obj.to_listing_dict()


def cache_refresh(session, refresher, *args, **kwargs):
    """Refresh the functions cache data in a new thread.

    Starts refreshing only after the session was committed.
    So all database data is available.
    """
    assert isinstance(session, Session), \
        'Need a session, not a sessionmaker or scoped_session'

    @event.listens_for(session, 'after_commit')
    def do_refresh(session):
        p = Process(target=refresher, args=args, kwargs=kwargs)
        p.start()
        p.join()


def handle_workflow_transition(event):
    """Handle workflow transition event."""
    # TODO: avoid executing this twice in the same request for the same object
    manager = getUtility(ICacheManager)
    obj = event.obj
    manager.refresh(obj)


class BaseCacheManager:
    """Base implementation of a cache manager Utility."""

    implements(ICacheManager)

    _config = {
        'expiration_time': 3600
    }
    _backend = 'dogpile.cache.memory'
    _region = None

    def refresh(self, obj):
        """Invalidate and refresh a given model object.."""
        region = self.region()
        session = object_session(obj)
        region.invalidate(obj)
        cache_refresh(session, refresher, obj)

    def _create_region(self):
        """Create a new region instance."""
        backend = self._backend
        config = self._config
        region = make_region(
            function_key_generator=self.key_generator
        ).configure(backend, **config,)
        return region

    def region(self, config):
        """Get the existing cache region."""
        _region = self._region
        if not _region:
            self._region = self._create_region()
        return _region

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
