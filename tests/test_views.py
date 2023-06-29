from django.test.testcases import TestCase
from django.urls import reverse
from django_twined.models import ServiceRevision


class TestServiceRevision(TestCase):
    def test_get_service_revision_with_revision_tag(self):
        """Test getting a service revision when the revision tag is supplied."""
        service_revision = ServiceRevision.objects.create(namespace="my-org", name="my-service", tag="1.0.0")

        response = self.client.get(
            reverse(
                "service-revisions",
                args=[service_revision.namespace, service_revision.name, service_revision.tag],
            ),
        )

        self.assertEqual(
            response.json(),
            {"name": "my-service", "namespace": "my-org", "revision_tag": "1.0.0", "success": True},
        )
