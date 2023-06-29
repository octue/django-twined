from django.conf.urls import include, re_path
from django.contrib import admin
from django_gcp import urls as django_gcp_urls


admin.autodiscover()
urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^gcp/", include(django_gcp_urls)),
    re_path(r"^integrations/octue/", include("django_twined.urls")),
]
