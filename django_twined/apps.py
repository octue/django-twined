from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoTwinedAppConfig(AppConfig):
    name = 'django_twined'
    label = 'django_twined'
    verbose_name = _('Django Twined')

    def ready(self):
        from django_twined.signals import register_signal_handlers
        register_signal_handlers()
