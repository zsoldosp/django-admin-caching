from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', include(admin.site.urls), {}, "admin-index"),
    # url(r'^some-path/$', some_view, {}, 'some_view'),
]
