from django.core.urlresolvers import resolve
from django.contrib.auth.models import Group
import pytest
from testapp.test_helpers import get_group_changelist_table


def test_the_admin_is_configured_working(admin_client, db):
    Group.objects.create(name='foo')
    assert resolve('/admin/') is not None
    assert resolve('/admin/auth/') is not None
    assert resolve('/admin/auth/group/') is not None
    headers, rows = get_group_changelist_table(admin_client)
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
