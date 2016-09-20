from django_admin_caching.caching import CacheConfig


def test_explicit_attribute_with_true_value_enables_caching():
    class WithCachingEnabled(object):
        admin_caching_enabled = True
    cfg = CacheConfig(model_admin=WithCachingEnabled())
    assert cfg.is_enabled is True


def test_explicit_attribute_with_false_value_disables_caching():
    class WithCachingDisabled(object):
        admin_caching_enabled = False
    cfg = CacheConfig(model_admin=WithCachingDisabled())
    assert cfg.is_enabled is False


def test_without_explicit_attribute_caching_is_disabled():
    class NoExplicitCacheEnabler(object):
        pass
    cfg = CacheConfig(model_admin=NoExplicitCacheEnabler())
    assert cfg.is_enabled is False
