from django.conf.urls import url
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls, {}, "admin-index"),
    # url(r'^some-path/$', some_view, {}, 'some_view'),
]
