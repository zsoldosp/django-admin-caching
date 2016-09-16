from django.contrib.admin.templatetags import admin_list
from django.core.cache import cache

def cached_items_for_result(orig, cl, result, form):
    cifr = CachedItemsForResult(orig=orig, cl=cl, result=result, form=form)
    return cifr.items_for_result()


class CachedItemsForResult(object):

    def __init__(self, orig, cl, result, form):
        self.orig = orig
        self.cl = cl
        self.result = result
        self.form = form

    def items_for_result(self):
        key = self.cache_key()
        if key not in cache:
            res = list(self.orig(self.cl, self.result, self.form))
            cache.set(key=key, value=res)
            return res
        return cache.get(key=key)

    def result_from_cache(self):
        key = self.cache_key()
        return cache.get(key=key)

    def cache_key(self):
        admin_cls = type(self.cl.model_admin)
        return '{}.{}-{}.{}-{}'.format(
            admin_cls.__module__,
            admin_cls.__name__,
            self.result._meta.app_label,
            type(self.result).__name__,
            self.result_cache_key()
        )

    def result_cache_key(self):
        custom_key = getattr(self.cl.model_admin, 'admin_caching_key', None)
        if custom_key:
            return custom_key(self.result)
        return '{}'.format(
            self.result.pk
        )
