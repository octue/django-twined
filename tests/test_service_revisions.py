# Disables for testing:
# pylint: disable=missing-docstring

from django.test import TestCase
from django_twined.models import ServiceRevision


class ServiceRevisionTestCase(TestCase):
    def test_topic(self):
        """Ensure that default settings are read for creating default entries in the db"""
        sr = ServiceRevision.objects.create(
            project_name="gargantuan-gibbons", namespace="large-gibbons", name="gibbon-analyser", tag="latest"
        )

        self.assertEqual(sr.topic, "octue.services.large-gibbons.gibbon-analyser")

    def test_create_with_defaults(self):
        """Ensure that default settings are read for creating default entries in the db"""

        sr = ServiceRevision.objects.create(
            name="gibbon-analyser",
        )

        self.assertEqual(sr.namespace, "test-default-namespace")
        self.assertEqual(sr.project_name, "test-default-project-name")
        self.assertEqual(sr.tag, "test-default-tag")
