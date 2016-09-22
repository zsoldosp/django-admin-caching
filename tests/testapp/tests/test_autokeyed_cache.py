from django.contrib.auth.models import Group, User
from django_admin_caching.caching import CacheKey, CacheConfig, AutoKeyedCache


def test_creates_the_correct_objects(django_caches):
    result = Group(name='result')
    model_admin = Group(name='admin')
    akc = AutoKeyedCache(result=result, model_admin=model_admin)
    assert isinstance(akc.ck, CacheKey)
    assert akc.ck.model_admin == model_admin
    assert akc.ck.result == result
    assert isinstance(akc.cfg, CacheConfig)
    assert akc.cfg.model_admin == model_admin


def test_get_set_uses_correct_cache(django_caches):
    result = Group(name='foo')
    akc = AutoKeyedCache(result=result)
    akc.set('sdf')
    assert akc.ck.key in akc.cfg.cache
    assert akc.cfg.cache.get(akc.ck.key) == 'sdf'
    assert 'sdf' == akc.get()


def test_can_be_created_without_a_model_admin_specified(django_caches):
    akc = AutoKeyedCache(result=Group(name='random'))
    assert akc.cfg.model_admin is not None
    assert akc.cfg.model_admin == akc.ck.model_admin


def test_has_value_works_correctly(django_caches):
    akc = AutoKeyedCache(result=Group(name='group'))
    assert not akc.has_value()
    akc.set('abcde')
    assert akc.has_value()


def test_akc_is_null_object_so_set_and_has_value_works(django_caches):
    class DisabledModelAdmin(object):
        admin_caching_enabled = False

    akc = AutoKeyedCache(
        result=Group(name='baz'), model_admin=DisabledModelAdmin())
    assert not akc.has_value()
    assert akc.ck.key not in akc.cfg.cache
    akc.set('sdf')  # should be a noop
    assert not akc.has_value()
    assert akc.ck.key not in akc.cfg.cache


def test_after_runtime_key_change_its_not_in_cache(django_caches):
    akc = AutoKeyedCache(result=Group(name='first key'))
    assert not akc.has_value()
    akc.set('abcde')
    assert akc.has_value()
    akc.ck.result.name = 'second key'
    assert not akc.has_value()


def test_can_remove_itself_from_the_cache(django_caches):
    akc = AutoKeyedCache(result=Group(name='key'))
    akc.cfg.cache.set('other key', 'other val')
    assert not akc.has_value()
    akc.set('foo')
    akc.delete()
    assert not akc.has_value()
    assert akc.ck.key not in akc.cfg.cache
    assert akc.cfg.cache.get('other key') == \
        'other val'  # don't remove unrelated entries


def test_can_remove_itself_from_cache_even_if_not_in_it(django_caches):
    akc = AutoKeyedCache(result=Group(name='key'))
    akc.cfg.cache.set('foo', 'foo')
    assert not akc.has_value()
    akc.delete()
    assert not akc.has_value()
    assert akc.cfg.cache.get('foo') == 'foo'  # don't remove unrelated entries


def test_works_with_object_that_isnt_enabled_for(django_caches):
    akc = AutoKeyedCache(result=User())
    assert not akc.cfg.is_enabled
    assert not akc.has_value()
