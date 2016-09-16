from django.contrib.auth.models import Group
from django.contrib.sessions.models import Session
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
        cached_item_for_result, admin_cls, result, expected_key):
    cached_item_for_result.cl.model_admin = admin_cls()
    cached_item_for_result.result = result
    assert cached_item_for_result.result_cache_key() == '{}'.format(result.pk)
    assert cached_item_for_result.cache_key() == expected_key


def test_can_provide_custom_override_to_cache_key_through_model_admin(
        cached_item_for_result):
    class AdminWithCustomCacheKey(object):
        def admin_caching_key(self, obj):
            return 'Foo:Bar:9'

    cached_item_for_result.cl.model_admin = AdminWithCustomCacheKey()
    cached_item_for_result.result = Group(pk=55)
    assert cached_item_for_result.result_cache_key() == 'Foo:Bar:9'
    assert cached_item_for_result.cache_key() == \
        '{}.AdminWithCustomCacheKey-auth.Group-Foo:Bar:9'.format(
            AdminWithCustomCacheKey.__module__)


def test_first_call_to_items_for_result_calls_orig_and_puts_it_to_cache(
        cached_item_for_result):
    cached_item_for_result.items_for_result()
    assert cached_item_for_result.orig.called
    cached_item_for_result.orig.assert_called_once_with(
        cached_item_for_result.cl, cached_item_for_result.result,
        cached_item_for_result.form)


def test_first_call_puts_results_into_cache_and_can_read_it_from(
        cached_item_for_result, django_caches):
    first_result = list(cached_item_for_result.items_for_result())
    cache = django_caches['default']
    cache_key = cached_item_for_result.cache_key()
    assert cache_key in cache
    assert cache.get(cache_key)
    result_from_cache = list(cached_item_for_result.result_from_cache())
    assert first_result == result_from_cache


def test_second_call_for_unchanged_key_returns_cached_witout_calling_orig(
        cached_item_for_result, django_caches):
    first_result = list(cached_item_for_result.items_for_result())
    cached_item_for_result.orig.reset_mock()
    assert not cached_item_for_result.orig.called
    second_result = list(cached_item_for_result.items_for_result())
    assert not cached_item_for_result.orig.called
    assert first_result == second_result


def test_should_key_change_it_calls_again_original(
        cached_item_for_result, django_caches):
    class AdminWithCustomCacheKey(object):
        def admin_caching_key(self, obj):
            return obj.name

    cached_item_for_result.result.name = 'first'
    cached_item_for_result.cl.model_admin = AdminWithCustomCacheKey()
    cached_item_for_result.items_for_result()
    cached_item_for_result.orig.reset_mock()

    cached_item_for_result.result.name = 'second'
    cached_item_for_result.items_for_result()
    assert cached_item_for_result.orig.called
    cached_item_for_result.orig.assert_called_once_with(
        cached_item_for_result.cl, cached_item_for_result.result,
        cached_item_for_result.form)
