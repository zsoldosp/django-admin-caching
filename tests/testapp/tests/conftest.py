from django.contrib.admin.sites import site
from django.contrib.auth.models import Group
from django.core.cache import caches
from django_admin_caching.admin_row import CachedItemsForResult
import pytest
from testapp.six import patch, Mock
from testapp.test_helpers import get_group_changelist_table


@pytest.fixture()
def django_caches():
    yield caches
    # finalizer
    for cache in caches.all():
        cache.clear()


@pytest.fixture()
def capitalized_name_mock():
    admin = site._registry[Group]
    mock = patch.object(admin, 'capitalized_name', autospec=True)
    yield mock.start()
    mock.stop()


@pytest.fixture()
def myadmin_cl_table(db, admin_client):
    return lambda: get_group_changelist_table(admin_client)


@pytest.fixture()
def cached_item_for_result():
    cl_mock = Mock()
    model_obj = Group(pk=2)
    orig_mock = Mock()
    orig_mock.return_value = ['1', '2', '3']
    return CachedItemsForResult(
        orig=orig_mock, cl=cl_mock, result=model_obj, form=None)
