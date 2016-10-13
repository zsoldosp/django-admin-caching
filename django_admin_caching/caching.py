from django.conf import settings
from django.contrib.admin.sites import site
from django.core import cache
from django.utils import translation


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
    def cache_timeout(self):
        return getattr(
            self.model_admin, 'admin_caching_timeout_seconds',
            self.cache.default_timeout)

    @property
    def cache(self):
        return cache.caches[self.cache_to_use_name()]


class CacheKey(object):
    def __init__(self, result, model_admin=None):
        if model_admin is None:
            self.model_admin = site._registry.get(type(result))
        else:
            self.model_admin = model_admin
        self.result = result

    @property
    def key(self):
        admin_cls = type(self.model_admin)
        parts = [
            self.i18n_l10n_prefix,
            admin_cls.__module__,
            admin_cls.__name__,
        ]
        beginning = '.'.join(p for p in parts if p)
        return '{}-{}.{}-{}'.format(
            beginning,
            self.result._meta.app_label,
            type(self.result).__name__,
            self.result_key()
        )

    @property
    def i18n_l10n_prefix(self):
        lang = translation.get_language()
        locale = translation.to_locale(lang)
        parts = []
        if settings.USE_I18N:
            parts += [lang]
        if settings.USE_L10N:
            parts += [locale]
        return '.'.join(parts)

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
        if self.cfg.is_enabled:
            self.cfg.cache.set(
                key=self.ck.key, value=value,
                timeout=self.cfg.cache_timeout)

    def get(self):
        return self.cfg.cache.get(key=self.ck.key)

    def has_value(self):
        return self.cfg.is_enabled and self.ck.key in self.cfg.cache

    def delete(self):
        if self.cfg.is_enabled:
            self.cfg.cache.delete(key=self.ck.key)
