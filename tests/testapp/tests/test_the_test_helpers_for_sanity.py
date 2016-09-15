from django.core.urlresolvers import resolve
from django.contrib.admin.sites import site
from django.contrib.auth.models import Group
import pytest
from testapp.six import patch


def test_the_admin_is_configured_working(myadmin_cl_table):
    Group.objects.create(name='foo')
    assert resolve('/admin/') is not None
    assert resolve('/admin/auth/') is not None
    assert resolve('/admin/auth/group/') is not None
    headers, rows = myadmin_cl_table()
    assert ['', 'Name', 'Capitalized name'] == headers
    assert len(rows) == 1
    assert ['', 'foo', 'Foo'] == rows[0]


@pytest.mark.parametrize('i', [1, 2])
def test_caches_fixture_provides_an_empty_cache(django_caches, i):
    key = 'foo'
    for cache in django_caches.all():
        assert key not in cache
        cache.set(key=key, value=i)
        assert key in cache
        assert cache.get(key) == i


def test_can_mock_custom_method_on_mygroupadmin(myadmin_cl_table):
    Group.objects.create(name='foo')
    admin = site._registry[Group]
    with patch.object(admin, 'capitalized_name') as capitalized_name_mock:
        capitalized_name_mock.boolean = False
        capitalized_name_mock.return_value = 'bar'
        headers, rows = myadmin_cl_table()
        assert rows == [['', 'foo', 'bar']]
    assert capitalized_name_mock.called
    assert 1 == capitalized_name_mock.call_count


def test_can_use_mocked_mygroupadmin_capitalized_name_fixture(
        myadmin_cl_table, capitalized_name_mock):
    Group.objects.create(name='abc')
    # assert root cause for failure in
    # django/contrib/admin/templatetags/admin_list.py
    assert not getattr(capitalized_name_mock, 'boolean', False)
    capitalized_name_mock.return_value = 'xyz'
    headers, rows = myadmin_cl_table()
    assert rows == [['', 'abc', 'xyz']]
    assert capitalized_name_mock.called
    assert 1 == capitalized_name_mock.call_count
