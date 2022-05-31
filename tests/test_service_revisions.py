# Disables for testing:
# pylint: disable=missing-docstring

import uuid
from django.test import TestCase
from django_twined.models import ServiceRevision


class ServiceRevisionTestCase(TestCase):
    def test_topic(self):
        """Ensure that default settings are read for creating default entries in the db"""
        topic_id = uuid.uuid4()
        sr = ServiceRevision.objects.create(
            topic_id=topic_id,
            project_name="gargantuan-gibbons",
            namespace="large-gibbons-r-us",
            name="gibbon-analyser",
        )

        self.assertEqual(sr.topic, f"octue.services.{topic_id}")

    def test_create_with_defaults(self):
        """Ensure that default settings are read for creating default entries in the db"""

        sr = ServiceRevision.objects.create(
            topic_id=uuid.uuid4(),
            name="gibbon-analyser",
        )

        self.assertEqual(sr.namespace, "test-default-namespace")
        self.assertEqual(sr.project_name, "test-default-project-name")
        self.assertEqual(sr.tag, "test-default-tag")
