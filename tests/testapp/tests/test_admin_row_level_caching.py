from django.contrib.auth.models import Group
from django.contrib.admin.templatetags import admin_list
from django_admin_caching.patching import Patched
from django_admin_caching.admin_row import \
    CachedItemsForResult, cached_items_for_result
import pytest
from testapp.sixmocks import patch, DEFAULT, call


@pytest.mark.acceptance
def test_caches_admin_row(
        myadmin_cl_table, capitalized_name_mock):
    foo = Group.objects.create(name='foo')
    bar = Group.objects.create(name='bar')
    baz = Group.objects.create(name='baz')
    capitalized_name_mock.return_value = 'xyz'

    uncached_headers, uncached_rows = myadmin_cl_table()
    assert uncached_rows == [
        ['', 'baz', 'xyz'],
        ['', 'bar', 'xyz'],
        ['', 'foo', 'xyz'],
    ]
    assert 3 == capitalized_name_mock.call_count
    capitalized_name_mock.assert_has_calls(
        [call(baz), call(bar), call(foo)],
        any_order=False
    )

    capitalized_name_mock.reset_mock()
    cached_headers, cached_rows = myadmin_cl_table()
    assert 0 == capitalized_name_mock.call_count, 'no new calls'
    assert uncached_headers == cached_headers
    assert uncached_rows == cached_rows

    foo.name = 'FOO'
    foo.save()
    capitalized_name_mock.reset_mock()
    partly_cached_headers, partly_cached_rows = myadmin_cl_table()
    assert 1 == capitalized_name_mock.call_count, 'no new calls'
    capitalized_name_mock.assert_has_calls(
        [call(foo)],
        any_order=False
    )
    assert uncached_headers == partly_cached_headers
    assert partly_cached_rows == [
        ['', 'baz', 'xyz'],
        ['', 'bar', 'xyz'],
        ['', 'FOO', 'xyz'],
    ]


def test_admin_list_items_for_result_is_patched_by_app():
    assert isinstance(admin_list.items_for_result, Patched)
    orig = admin_list.items_for_result.orig
    new = admin_list.items_for_result.new
    assert orig.__code__.co_filename == \
        admin_list.paginator_number.__code__.co_filename
    assert new == cached_items_for_result
    assert get_argnames(new) == ('orig', ) + get_argnames(orig)


def test_wrapper_fn_calls_class_tested_below():
    mocks = patch.multiple(
        CachedItemsForResult, __init__=DEFAULT, items_for_result=DEFAULT)
    with mocks as cifr_mocks:
        cifr_mocks['__init__'].return_value = None
        orig = object()
        cl = object()
        result = object()
        form = object()
        cached_items_for_result(orig=orig, cl=cl, result=result, form=form)
    assert cifr_mocks['__init__'].called
    cifr_mocks['__init__'].assert_called_once_with(
        orig=orig, cl=cl, result=result, form=form)
    assert cifr_mocks['items_for_result'].called
    cifr_mocks['items_for_result'].assert_called_once_with()


def get_argnames(fn):
    return fn.__code__.co_varnames[:fn.__code__.co_argcount]


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
    result_from_cache = list(cached_item_for_result.from_cache())
    assert first_result == result_from_cache


def test_second_call_for_unchanged_key_returns_cached_witout_calling_orig(
        cached_item_for_result, django_caches):
    first_result = list(cached_item_for_result.items_for_result())
    cached_item_for_result.orig.reset_mock()
    second_result = list(cached_item_for_result.items_for_result())
    assert not cached_item_for_result.orig.called
    assert first_result == second_result






