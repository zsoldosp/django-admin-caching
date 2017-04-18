import django
from django.apps import AppConfig
from django.db.models.signals import post_save
from django.contrib.admin.templatetags import admin_list
from django_admin_caching.admin_row import PatchedAdminListItemsForResult
from django_admin_caching.signals import \
    auto_delete_from_cache_on_model_post_save


class DjangoAdminCachingAppConfig(AppConfig):

    name = 'django_admin_caching'

    def ready(self):
        if django.VERSION[:2] == (1, 9):
            import warnings
            msg = "You are using an unsupported Django version. " \
                  "django-admin-caching support" \
                  " might be dropped in any following release. See " \
                  "https://www.djangoproject.com/download/#supported-versions"
            warnings.warn(msg)

        admin_list.items_for_result = PatchedAdminListItemsForResult()
        post_save.connect(auto_delete_from_cache_on_model_post_save)
