from django.contrib.admin.templatetags import admin_list
from django_admin_caching.caching import AutoKeyedCache
from django_admin_caching.patching import Patched


class PatchedAdminListItemsForResult(Patched):

    auto_keyed_cache_cls = AutoKeyedCache

    def __init__(self):
        super(PatchedAdminListItemsForResult, self).__init__(
            orig=admin_list.items_for_result,
            new=self.cached_items_for_result
        )

    def to_akc(self, cl, result):
        return self.auto_keyed_cache_cls(
            model_admin=cl.model_admin, result=result)

    def cached_items_for_result(self, orig, cl, result, form):
        akc = self.to_akc(cl=cl, result=result)
        if akc.has_value():
            return akc.get()
        res = list(orig(cl=cl, result=result, form=form))
        akc.set(res)
        return res
