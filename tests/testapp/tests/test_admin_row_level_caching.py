from django.contrib.auth.models import Group
from django.contrib.admin.templatetags import admin_list
from django_admin_caching.admin_row import PatchedAdminListItemsForResult
import pytest
from testapp.sixmocks import Mock, call


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
    assert isinstance(
        admin_list.items_for_result, PatchedAdminListItemsForResult)
    orig = admin_list.items_for_result.orig
    new = admin_list.items_for_result.new
    assert orig.__code__.co_filename == \
        admin_list.paginator_number.__code__.co_filename
    assert new == admin_list.items_for_result.cached_items_for_result
    assert get_argnames(new) == ('self', 'orig', ) + get_argnames(orig)


def get_argnames(fn):
    return fn.__code__.co_varnames[:fn.__code__.co_argcount]


@pytest.fixture()
def palifr():
    class MockedPatchedAdminListItemsForResult(PatchedAdminListItemsForResult):

        def __init__(self):
            super(MockedPatchedAdminListItemsForResult, self).__init__()
            self.orig = Mock(name='orig list items for result')
            self.orig.return_value = ['rendered', 'parts']
            self.to_akc = Mock(name='to akc factory method')
            self.akc_mock = Mock(name='the actual akc mock')
            self.to_akc.return_value = self.akc_mock

        @property
        def all_mocks(self):
            return [self.to_akc, self.orig, self.akc_mock]

        def foreach_mock(self, fn):
            for mock in self.all_mocks:
                fn(mock)

    obj = MockedPatchedAdminListItemsForResult()
    obj.foreach_mock(lambda m: m.start())
    yield obj
    obj.foreach_mock(lambda m: m.stop())


def test_if_not_in_cache_calls_orig_and_caches(palifr):
    cl = object()
    result = object()
    form = object()

    palifr.akc_mock.has_value.return_value = False
    rendered = palifr(cl=cl, result=result, form=form)

    palifr.to_akc.assert_called_once_with(cl=cl, result=result)
    palifr.akc_mock.has_value.assert_called_once_with()
    palifr.orig.assert_called_once_with(cl=cl, result=result, form=form)
    palifr.akc_mock.set.assert_called_once_with(rendered)
    assert not palifr.akc_mock.get.called


def test_if_cache_has_item_it_is_returned_from_there(palifr):
    cl = object()
    result = object()
    form = object()

    palifr.akc_mock.has_value.return_value = True
    palifr.akc_mock.get.return_value = ['cached', 'rendered', 'items']

    second_rendered = palifr(cl=cl, result=result, form=form)
    assert second_rendered == ['cached', 'rendered', 'items']
    palifr.to_akc.assert_called_once_with(cl=cl, result=result)
    palifr.akc_mock.has_value.assert_called_once_with()
    assert not palifr.orig.called
    assert not palifr.akc_mock.set.called
    palifr.akc_mock.get.assert_called_once_with()
