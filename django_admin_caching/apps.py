from django.apps import AppConfig
from django.contrib.admin.templatetags import admin_list
from django_admin_caching.admin_row import cached_items_for_result
from django_admin_caching.patching import Patched


class DjangoAdminCachingAppConfig(AppConfig):

    name = 'django_admin_caching'

    def ready(self):
        admin_list.items_for_result = Patched(
            orig=admin_list.items_for_result,
            new=cached_items_for_result,
        )
