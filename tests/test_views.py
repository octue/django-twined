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
            {"namespace": "my-org", "name": "my-service", "revision_tag": "1.0.0", "success": True},
        )

    def test_get_service_revision_without_revision_tag(self):
        """Test that the latest service revision is returned when the revision tag isn't supplied."""
        namespace = "my-org"
        name = "my-service"

        ServiceRevision.objects.create(namespace=namespace, name=name, tag="0.1.0")
        ServiceRevision.objects.create(namespace=namespace, name=name, tag="1.0.0")
        latest_service_revision = ServiceRevision.objects.create(namespace=namespace, name=name, tag="1.0.1")

        response = self.client.get(reverse("service-revisions", kwargs={"namespace": namespace, "name": name}))

        self.assertEqual(
            response.json(),
            {"namespace": namespace, "name": name, "revision_tag": latest_service_revision.tag, "success": True},
        )
