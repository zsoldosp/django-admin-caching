from django_admin_caching.caching import AutoKeyedCache


def auto_delete_from_cache_on_model_post_save(sender, signal, **kwargs):
    instance = kwargs['instance']
    AutoKeyedCache(result=instance).delete()
