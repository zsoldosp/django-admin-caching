from django.apps import AppConfig
from django.contrib.admin.templatetags import admin_list
from django_admin_caching.admin_row import PatchedAdminListItemsForResult


class DjangoAdminCachingAppConfig(AppConfig):

    name = 'django_admin_caching'

    def ready(self):
        admin_list.items_for_result = PatchedAdminListItemsForResult()
