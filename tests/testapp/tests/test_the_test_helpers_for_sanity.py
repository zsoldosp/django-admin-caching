from django.core.urlresolvers import resolve
from django.contrib.auth.models import Group
from testapp.test_helpers import parse_table


def test_the_admin_is_configured_working(admin_client, db):
    Group.objects.create(name='foo')
    assert resolve('/admin/') is not None
    assert resolve('/admin/auth/') is not None
    assert resolve('/admin/auth/group/') is not None
    response = admin_client.get('/admin/auth/group/')
    assert response.status_code == 200
    headers, rows = parse_table(response)
    assert ['', 'Name', 'Capitalized name'] == headers
    assert len(rows) == 1
    assert ['', 'foo', 'Foo'] == rows[0]
