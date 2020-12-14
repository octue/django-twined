from django.conf.urls import url
from django.contrib import admin
from django_twined.consumers.service import ServiceConsumer


admin.autodiscover()


urlpatterns = [url(r"^admin/", admin.site.urls), url(r"^my-consumer/$", ServiceConsumer.as_asgi())]
