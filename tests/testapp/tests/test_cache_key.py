from django.contrib.auth.models import Group
from django.contrib.sessions.models import Session
from django_admin_caching.caching import CacheKey
import pytest


@pytest.mark.parametrize(
    'admin_cls,result,expected_key', [
        (Session, Group(pk=3),
         'django.contrib.sessions.models.Session-auth.Group-3'),
        (Group, Group(pk=5),
         'django.contrib.auth.models.Group-auth.Group-5'),
    ]
)
def test_cache_key_is_derived_from_admin_and_obj_by_default(
        admin_cls, result, expected_key):
    ck = CacheKey(model_admin=admin_cls(), result=result)
    assert ck.result_key() == '{}'.format(result.pk)
    assert ck.key == expected_key


def test_can_provide_custom_override_to_cache_key_through_model_admin():
    class AdminWithCustomCacheKey(object):
        def admin_caching_key(self, obj):
            return 'Foo:Bar:9'

    ck = CacheKey(model_admin=AdminWithCustomCacheKey(), result=Group(pk=55))
    assert ck.result_key() == 'Foo:Bar:9'
    assert ck.key == \
        '{}.AdminWithCustomCacheKey-auth.Group-Foo:Bar:9'.format(
            AdminWithCustomCacheKey.__module__)
