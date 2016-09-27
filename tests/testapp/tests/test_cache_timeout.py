from django.core import cache
from django_admin_caching.caching import CacheConfig, AutoKeyedCache
from testapp.sixmock import patch, Mock


class TestTimeoutIsSpecifiedFromModelAdminsProperty(object):
    def test_when_nothing_is_provided_caches_default_will_be_used(self):
        no_attribute_model_admin = object()
        cfg = CacheConfig(model_admin=no_attribute_model_admin)
        assert cfg.cache_timeout == cache.caches['default'].default_timeout

    def test_when_attribute_is_provided_that_is_used_to_add_to_autocache(self):
        class WithValidTimeout(object):
            admin_caching_timeout_seconds = 60 * 60 * 2  # 2 hours
        cfg = CacheConfig(model_admin=WithValidTimeout())
        assert cfg.cache_timeout == 60 * 60 * 2


def test_configs_cache_timeout_is_passed_on_to_cache_set_method():
    class MockAdmin(object):
        admin_caching_timeout_seconds = Mock()
        admin_caching_enabled = True

    with patch.object(CacheConfig, 'cache') as cache_mock:
        akc = AutoKeyedCache(result=Mock(), model_admin=MockAdmin())
        akc.set('foo')
    cache_mock.set.assert_called_once_with(
        key=akc.ck.key, value='foo',
        timeout=MockAdmin.admin_caching_timeout_seconds)
