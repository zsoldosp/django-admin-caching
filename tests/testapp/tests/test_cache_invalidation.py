from django.contrib.auth.models import Group
from django_admin_caching.caching import AutoKeyedCache
from django_admin_caching.signals import \
    auto_delete_from_cache_on_model_post_save


def test_signal_handler_removes_item_from_cache(django_caches):
    g = Group(name='group')
    akc = AutoKeyedCache(result=g)
    akc.cfg.cache.set('foo', 'foo')
    akc.set('value')
    auto_delete_from_cache_on_model_post_save(
        sender=None, signal=None, instance=g)
    assert not akc.has_value()
    assert akc.cfg.cache.get('foo') == 'foo'


def test_when_object_present_in_cache_saved_it_is_removed(db, django_caches):
    g = Group(name='foo')
    akc = AutoKeyedCache(result=g)
    assert not akc.has_value()
    akc.set('cached val')
    g.save()
    assert not akc.has_value()
