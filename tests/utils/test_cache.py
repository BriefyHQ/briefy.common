from briefy.common.utils.cache import _make_cache_key
from briefy.common.utils.cache import timeout_cache

import pytest
import time


def test_make_key():
    key = _make_cache_key(0, 1, first='thing', we='do')

    assert hash(key)

    key2 = _make_cache_key(0, 1, first='we', we='thing')

    assert key != key2

    key3 = _make_cache_key(0, 1, we='do', first='thing')

    assert key == key3

    with pytest.raises(TypeError):
        _make_cache_key([])


def test_timeout_cache_basic():
    called = False

    @timeout_cache(0.02)
    def cached(a, b, c=0, **kw):
        nonlocal called
        called = True
        return a, b, c, kw

    res = cached(1, 2)

    assert res == (1, 2, 0, {})
    assert called

    called = False
    res = cached(1, 2)

    assert res == (1, 2, 0, {})
    assert not called

    called = False
    time.sleep(0.03)
    res = cached(1, 2)

    assert res == (1, 2, 0, {})
    assert called


def test_timeout_cache_doesnotcache_unhashable_parameters():
    called = False

    @timeout_cache(0.02)
    def cached(a):
        nonlocal called
        called = True
        return a

    cached([1])
    assert called

    called = False
    cached([1])
    assert called


def test_timeout_cache_wont_mix_parameters():
    called = False

    @timeout_cache(0.02)
    def cached(a, b):
        nonlocal called
        called = True
        return a, b

    called = False
    res = cached(1, 2)
    assert res == (1, 2)
    assert called

    called = False
    res = cached(3, 4)
    assert res == (3, 4)
    assert called

    called = False
    res = cached(1, 2)
    assert res == (1, 2)
    assert not called

    called = False
    res = cached(3, 4)
    assert res == (3, 4)
    assert not called


def test_timeout_cache_renew():
    called = False

    @timeout_cache(0.02, False)
    def cached(a):
        nonlocal called
        called = True
        return a

    called = False
    res = cached(1)
    assert res == 1
    assert called

    time.sleep(0.01)
    called = False
    res = cached(1)
    assert res == 1
    assert not called

    time.sleep(0.0125)

    called = False
    res = cached(1)
    assert res == 1
    assert called

    @timeout_cache(0.02, True)
    def cached(a):
        nonlocal called
        called = True
        return a

    called = False
    res = cached(1)
    assert res == 1
    assert called

    time.sleep(0.01)
    called = False
    res = cached(1)
    assert res == 1
    assert not called

    time.sleep(0.0125)

    called = False
    res = cached(1)
    assert res == 1
    assert not called

    res = cached(2)
    assert res == 2
    assert called
