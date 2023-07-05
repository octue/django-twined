from django.urls import path
from django_twined.views import service_revision


urlpatterns = [
    path(r"services/<namespace>/<name>", service_revision, name="services"),
]
