from django.urls import path
from django_twined.views import service_revision


urlpatterns = [
    path(r"services/<namespace>/<name>/<revision_tag>", service_revision, name="service-revisions"),
    path(r"services/<namespace>/<name>", service_revision, name="service-revisions"),
]
