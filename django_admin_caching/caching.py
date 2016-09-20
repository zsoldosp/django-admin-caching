from django.contrib.admin.sites import site
from django.core.cache import caches


class CacheConfig(object):
    def __init__(self, model_admin):
        self.model_admin = model_admin

    @property
    def is_enabled(self):
        return getattr(self.model_admin, 'admin_caching_enabled', False)

    def cache_to_use_name(self):
        return getattr(
            self.model_admin, 'admin_caching_cache_name', 'default')

    @property
    def cache(self):
        return caches[self.cache_to_use_name()]


class CacheKey(object):
    def __init__(self, result, model_admin=None):
        if model_admin is None:
            self.model_admin = site._registry[type(result)]
        else:
            self.model_admin = model_admin
        self.result = result

    @property
    def key(self):
        admin_cls = type(self.model_admin)
        return '{}.{}-{}.{}-{}'.format(
            admin_cls.__module__,
            admin_cls.__name__,
            self.result._meta.app_label,
            type(self.result).__name__,
            self.result_key()
        )

    def result_key(self):
        custom_key = getattr(self.model_admin, 'admin_caching_key', None)
        if custom_key:
            return custom_key(self.result)
        return '{}'.format(
            self.result.pk
        )


class AutoKeyedCache(object):

    def __init__(self, result, model_admin=None):
        self.ck = CacheKey(result=result, model_admin=model_admin)
        self.cfg = CacheConfig(model_admin=self.ck.model_admin)

    def set(self, value):
        self.cfg.cache.set(key=self.ck.key, value=value)

    def get(self):
        return self.cfg.cache.get(key=self.ck.key)

    def has_value(self):
        return self.ck.key in self.cfg.cache
