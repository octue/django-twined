# Disable these to allow import of the signals on app eady callback
# pylint: disable=import-outside-toplevel,unused-import

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoTwinedAppConfig(AppConfig):
    """Configuration and signal registration for the django_twined app"""

    name = "django_twined"
    label = "django_twined"
    verbose_name = _("Django Twined")

    def ready(self):
        import django_twined.signals  # noqa:F401
