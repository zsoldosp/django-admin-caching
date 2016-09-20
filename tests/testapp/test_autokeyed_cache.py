from django.contrib.auth.models import Group
from django_admin_caching.caching import CacheKey, CacheConfig, AutoKeyedCache


def test_creates_the_correct_objects():
    result = Group(pk=1)
    model_admin = Group(pk=2)
    akc = AutoKeyedCache(result=result, model_admin=model_admin)
    assert isinstance(akc.ck, CacheKey)
    assert akc.ck.model_admin == model_admin
    assert akc.ck.result == result
    assert isinstance(akc.cfg, CacheConfig)
    assert akc.cfg.model_admin == model_admin


def test_get_set_uses_correct_cache():
    result = Group(pk=1)
    model_admin = Group(pk=2)
    akc = AutoKeyedCache(result=result, model_admin=model_admin)
    akc.set('sdf')
    assert akc.ck.key in akc.cfg.cache
    assert akc.cfg.cache.get(akc.ck.key) == 'sdf'
    assert 'sdf' == akc.get()


def test_can_be_created_without_a_model_admin_specified():
    akc = AutoKeyedCache(result=Group(pk=3))
    assert akc.cfg.model_admin is not None
    assert akc.cfg.model_admin == akc.ck.model_admin


def test_has_value_works_correctly():
    akc = AutoKeyedCache(result=Group(pk=3))
    assert not akc.has_value()
    akc.set('abcde')
    assert akc.has_value()
