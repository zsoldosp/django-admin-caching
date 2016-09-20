from django.contrib.admin.sites import site


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
