from django.apps import AppConfig
from django.db.models.signals import post_save
from django.contrib.admin.templatetags import admin_list
from django_admin_caching.admin_row import PatchedAdminListItemsForResult
from django_admin_caching.signals import \
    auto_delete_from_cache_on_model_post_save


class DjangoAdminCachingAppConfig(AppConfig):

    name = 'django_admin_caching'

    def ready(self):
        admin_list.items_for_result = PatchedAdminListItemsForResult()
        post_save.connect(auto_delete_from_cache_on_model_post_save)
