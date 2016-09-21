"""Helpers to deal with cache."""
from collections import namedtuple
from functools import wraps

import logging
import time

logger = logging.getLogger(__name__)


TimeStampedResult = namedtuple("TimeStampedResult", 'timestamp result')


def _make_cache_key(*args, **kw):
    """Internal function to make a cache key based on parameters passed to a cache function.

    Raises TypeError on unhashable parameters
    """
    key = args + (frozenset(kw.items()),)
    # Force raising of typeerror if unsuitable arguments:
    hash(key)
    return key


def timeout_cache(timeout, renew=False):
    """Decorate a function so that it is naively cached when called with the same parameters again.

    Similar to functools.lru_cache, but cache contents expire
    after `timeout`seconds (which can be fractional)

    Cache is kept in an in memory, in process (thread shared) dictionary
    *warning* This is a simple implementation, and should not be relied
    for timeouts under 1/100 second (even because it may add overhead
    on that magnitude of time)  It also does not take care of
    freeing references to expired contents - (except on new calls
    with the same parameters, of course)

    :param timeout: Timeout in second to expire the cached result
    :type timeout: float
    :param renew: wether a new call within the timout limit resets the
    timeout count for that parameter set
    :type renew: bool
    :rtype: decorated callable
    """
    def decorator(func):
        cache = {}

        @wraps(func)
        def wrapper(*args, **kw):
            local_renew = renew
            try:
                key = _make_cache_key(*args, **kw)
            except TypeError:
                # Uncacheable parameters
                logger.warn('Failed to cache call to \'{}\': unhashable parameters!'.format(
                    func.__name__))
                return func(*args, **kw)
            if key in cache and time.monotonic() - cache[key].timestamp < timeout:
                result = cache[key].result
            else:
                result = func(*args, **kw)
                local_renew = True
            if local_renew:
                cache[key] = TimeStampedResult(time.monotonic(), result)
            return result
        return wrapper
    return decorator
