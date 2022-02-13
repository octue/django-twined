# Disables for testing:
# pylint: disable=missing-docstring

from django.conf import settings
from django.test import TestCase
from django_twined.models import RegisteredService

from .mixins import CallCommandMixin


class ServiceRegistrationTestCase(CallCommandMixin, TestCase):
    def setUp(self):
        # This will be used to ensure the setting actually has a value
        self.num_services = len(settings.TWINED_SERVICES)
        if self.num_services == 0:
            raise ValueError("There must be at least one service defined in settings.TWINED_SERVICES to run tests")
        self.services = settings.TWINED_SERVICES
        super().setUp()

    def test_register_services(self):
        self.assertIs(RegisteredService.objects.count(), 0)
        self.callCommand("register_services")
        self.assertIs(RegisteredService.objects.count(), self.num_services)

    def test_reregistering_services_does_not_duplicate(self):
        self.assertIs(RegisteredService.objects.count(), 0)
        self.callCommand("register_services")
        self.callCommand("register_services")
        self.assertIs(RegisteredService.objects.count(), self.num_services)
