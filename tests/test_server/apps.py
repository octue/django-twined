from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoTwinedTestAppConfig(AppConfig):
    """App configuration for django-twined"""

    name = "tests"
    label = "tests"
    verbose_name = _("Django Twined Test App")
