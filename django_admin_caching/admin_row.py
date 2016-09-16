from django.core.cache import caches


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
        return getattr(self.cl.model_admin, 'do_admin_caching', None)

    def cache_key(self):
        admin_cls = type(self.cl.model_admin)
        return '{}.{}-{}.{}-{}'.format(
            admin_cls.__module__,
            admin_cls.__name__,
            self.result._meta.app_label,
            type(self.result).__name__,
            self.result_cache_key()
        )

    def cache_to_use(self):
        return caches[self.cache_to_use_name()]

    def cache_to_use_name(self):
        return getattr(
            self.cl.model_admin, 'admin_caching_cache_name', 'default')

    def result_cache_key(self):
        custom_key = getattr(self.cl.model_admin, 'admin_caching_key', None)
        if custom_key:
            return custom_key(self.result)
        return '{}'.format(
            self.result.pk
        )
