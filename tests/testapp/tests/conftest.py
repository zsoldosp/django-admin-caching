import pytest
from django.core.cache import caches


@pytest.fixture()
def django_caches():
    yield caches
    # finalizer
    for cache in caches.all():
        cache.clear()
