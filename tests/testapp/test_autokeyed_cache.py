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
