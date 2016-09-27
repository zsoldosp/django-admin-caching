from django.core import cache
from django.core.cache.backends.dummy import DummyCache
from django.core.cache.backends.base import InvalidCacheBackendError
from django.test.utils import override_settings
from django_admin_caching.caching import CacheConfig
import pytest
from testapp.sixmock import patch


class TestAdminClassCanSpecifyWhichCacheToUse(object):
    def test_nothing_specified_default_cache_is_used(self):
        class NoAttributeAdmin(object):
            pass
        cfg = CacheConfig(model_admin=NoAttributeAdmin())
        assert cfg.cache_to_use_name() == 'default'
        assert cfg.cache == cache.caches['default']

    def test_specified_cache_is_used(self):
        class AttributeSpecifiesCacheToUse(object):
            admin_caching_cache_name = 'foo'
        with self.caches('foo'):
            cfg = CacheConfig(model_admin=AttributeSpecifiesCacheToUse())
            assert cfg.cache_to_use_name() == 'foo'
            assert cfg.cache == cache.caches['foo']

    def test_if_wrong_cache_is_specified_there_is_an_error(self):
        class AttributeSpecifiesCacheToUse(object):
            admin_caching_cache_name = 'bar'
        with self.caches('default'):
            cfg = CacheConfig(model_admin=AttributeSpecifiesCacheToUse())
            with pytest.raises(InvalidCacheBackendError):
                cfg.cache   # accessing the cache

    def test_allows_other_apps_to_wrap_the_cache(self, django_caches):
        manual_cache = DummyCache('dummy', {})
        to_patch = 'django.core.cache.CacheHandler.__getitem__'
        with patch(to_patch, return_value=manual_cache) as mock:
            cfg = CacheConfig(model_admin=None)
            assert cache.caches['default'] == manual_cache
            assert cfg.cache == manual_cache
            assert mock.called

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
