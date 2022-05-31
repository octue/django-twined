from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ExampleAppConfig(AppConfig):
    """Example (test server) app configuration for django-twined"""

    name = "tests.server.example"
    label = "example"
    verbose_name = _("Django Twined Example / Test App")
