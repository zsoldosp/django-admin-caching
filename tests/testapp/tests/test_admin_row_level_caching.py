from django.contrib.auth.models import Group
from django.contrib.admin.templatetags import admin_list
from django.contrib.sessions.models import Session
from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError
from django.test.utils import override_settings
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
    result_from_cache = list(cached_item_for_result.from_cache())
    assert first_result == result_from_cache


def test_second_call_for_unchanged_key_returns_cached_witout_calling_orig(
        cached_item_for_result, django_caches):
    first_result = list(cached_item_for_result.items_for_result())
    cached_item_for_result.orig.reset_mock()
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


class TestCachingOnlyAppliesWhenAdminClassIsMarkedAsSuch(object):

    def test_explicit_attribute_is_true(self, cached_item_for_result,
                                        django_caches):
        cached_item_for_result.cl.model_admin.admin_caching_enabled = True
        assert cached_item_for_result.should_cache()
        cached_item_for_result.items_for_result()
        assert cached_item_for_result.orig.called
        cached_item_for_result.orig.reset_mock()
        cached_item_for_result.items_for_result()
        assert not cached_item_for_result.orig.called

    def test_explicit_attribute_is_false(self, cached_item_for_result,
                                         django_caches):
        cached_item_for_result.cl.model_admin.admin_caching_enabled = False
        cached_item_for_result.items_for_result()
        assert not cached_item_for_result.should_cache()
        assert cached_item_for_result.orig.called
        cached_item_for_result.orig.reset_mock()
        cached_item_for_result.items_for_result()
        assert cached_item_for_result.orig.called

    def test_has_no_attribute(self, cached_item_for_result, django_caches):
        class ModelAdmin(object):
            pass

        cached_item_for_result.cl.model_admin = ModelAdmin()
        assert not cached_item_for_result.should_cache()
        cached_item_for_result.items_for_result()
        assert cached_item_for_result.orig.called
        cached_item_for_result.orig.reset_mock()
        cached_item_for_result.items_for_result()
        assert cached_item_for_result.orig.called


class TestAdminClassCanSpecifyWhichCacheToUse(object):

    def test_nothing_specified_default_cache_is_used(self,
                                                     cached_item_for_result):
        class NoAttributeAdmin(object):
            pass

        cached_item_for_result.cl.model_admin = NoAttributeAdmin()
        assert cached_item_for_result.cache_to_use_name() == 'default'
        with self.caches('default', 'custom'):
            cached_item_for_result.cache('some result')
            key = cached_item_for_result.cache_key()
            assert key in caches['default']
            assert cached_item_for_result.from_cache() == 'some result'
            assert key not in caches['custom']

    def test_specified_cache_is_used(self, cached_item_for_result):
        cached_item_for_result.cl.model_admin.admin_caching_cache_name = 'foo'
        assert cached_item_for_result.cache_to_use_name() == 'foo'
        with self.caches('default', 'foo'):
            cached_item_for_result.cache('some result')
            key = cached_item_for_result.cache_key()
            assert key in caches['foo']
            assert cached_item_for_result.from_cache() == 'some result'
            assert key not in caches['default']

    def test_if_wrong_cache_is_specified_there_is_an_error(
            self, cached_item_for_result):
        cached_item_for_result.cl.model_admin.admin_caching_cache_name = \
            'no-such-cache'
        assert cached_item_for_result.cache_to_use_name() == 'no-such-cache'
        with self.caches('default', 'foo'):
            with pytest.raises(InvalidCacheBackendError):
                cached_item_for_result.cache('some result')

    class caches(override_settings):
        def __init__(self, *names):
            self.names = names
            self.caches_dict = dict(
                (name, {
                    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                    'LOCATION': name,
                })
                for name in names
            )
            super(
                TestAdminClassCanSpecifyWhichCacheToUse.caches, self).__init__(
                    CACHES=self.caches_dict)
