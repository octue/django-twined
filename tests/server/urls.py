from django.conf.urls import include, re_path, url
from django.contrib import admin
from django_gcp import urls as django_gcp_urls


admin.autodiscover()
urlpatterns = [url(r"^admin/", admin.site.urls), re_path(r"^gcp/", include(django_gcp_urls))]
