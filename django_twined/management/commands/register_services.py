import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django_twined.models import RegisteredService

from test.make import MakeMethodsMixin


logger = logging.getLogger(__name__)
User = get_user_model()


class Command(MakeMethodsMixin, BaseCommand):
    """Use `python manage.py help register_services` to display help for this command line administration tool"""

    help = "Registers the services available in settings into the database, enabling relation to services and asks."

    def handle(self, *args, **options):

        for service in settings.TWINED_SERVICES:
            RegisteredService.objects.get_or_create(id=service["topic_id"], name=service["service_name"])
