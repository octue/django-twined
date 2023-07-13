from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django_twined.views import service_revision


urlpatterns = [
    path(r"services/<namespace>/<name>", csrf_exempt(service_revision), name="services"),
]
