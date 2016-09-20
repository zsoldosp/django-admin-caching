from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError
from django.test.utils import override_settings
from django_admin_caching.caching import CacheConfig
import pytest


class TestAdminClassCanSpecifyWhichCacheToUse(object):
    def test_nothing_specified_default_cache_is_used(self):
        class NoAttributeAdmin(object):
            pass
        cfg = CacheConfig(model_admin=NoAttributeAdmin())
        assert cfg.cache_to_use_name() == 'default'
        assert cfg.cache == caches['default']

    def test_specified_cache_is_used(self):
        class AttributeSpecifiesCacheToUse(object):
            admin_caching_cache_name = 'foo'
        with self.caches('foo'):
            cfg = CacheConfig(model_admin=AttributeSpecifiesCacheToUse())
            assert cfg.cache_to_use_name() == 'foo'
            assert cfg.cache == caches['foo']

    def test_if_wrong_cache_is_specified_there_is_an_error(self):
        class AttributeSpecifiesCacheToUse(object):
            admin_caching_cache_name = 'bar'
        with self.caches('default'):
            cfg = CacheConfig(model_admin=AttributeSpecifiesCacheToUse())
            with pytest.raises(InvalidCacheBackendError):
                cfg.cache   # accessing the cache

    class caches(override_settings):
        def __init__(self, *names):
            self.names = names
            self.caches_dict = dict(
                (name, {
                    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                    'LOCATION': name,
                })
                for name in names
            )
            super(
                TestAdminClassCanSpecifyWhichCacheToUse.caches, self).__init__(
                    CACHES=self.caches_dict)
