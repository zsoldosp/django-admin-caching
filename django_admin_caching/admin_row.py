from django.core.cache import caches
from django_admin_caching.caching import CacheKey, CacheConfig


def cached_items_for_result(orig, cl, result, form):
    cifr = CachedItemsForResult(orig=orig, cl=cl, result=result, form=form)
    return cifr.items_for_result()


class CachedItemsForResult(object):

    def __init__(self, orig, cl, result, form):
        self.orig = orig
        self.cl = cl
        self.result = result
        self.form = form
        self.cache_key_obj = CacheKey(
            model_admin=cl.model_admin, result=result)
        self.cache_cfg = CacheConfig(model_admin=self.cl.model_admin)

    def items_for_result(self):
        if self.should_build():
            res = list(self.orig(self.cl, self.result, self.form))
            self.cache(res)
            return res
        return self.from_cache()

    def cache(self, res):
        self.cache_to_use().set(key=self.cache_key(), value=res)

    def from_cache(self):
        return self.cache_to_use().get(key=self.cache_key())

    def should_build(self):
        return not self.should_cache() or \
            self.cache_key() not in self.cache_to_use()

    def should_cache(self):
        return getattr(self.cl.model_admin, 'admin_caching_enabled', None)

    def cache_key(self):
        return self.cache_key_obj.key

    def cache_to_use(self):
        return caches[self.cache_to_use_name()]

    def cache_to_use_name(self):
        return self.cache_cfg.cache_to_use_name()
