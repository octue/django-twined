from django.test.testcases import TestCase
from django.urls import reverse
from django_twined.models import ServiceRevision


class TestServiceRevision(TestCase):
    def test_invalid_http_method_causes_error_response(self):
        """Test that an error response is returned if using an invalid HTTP method with the endpoint."""
        response = self.client.patch(reverse("service-revisions", args=["some", "service"]))
        self.assertEqual(response.json(), {"error": "Invalid request method."})

    def test_getting_nonexistent_service_revision_causes_error_response(self):
        """Test that an error response is returned if trying to get a non-existent service."""
        response = self.client.get(
            reverse("service-revisions", args=["non-existent", "service"]),
            data={"revision_tag": "latest"},
        )
        self.assertEqual(response.json(), {"error": "Service revision not found."})

    def test_get_service_revision_with_revision_tag(self):
        """Test getting a service revision when the revision tag is supplied."""
        service_revision = ServiceRevision.objects.create(namespace="my-org", name="my-service", tag="1.0.0")

        response = self.client.get(
            reverse(
                "service-revisions",
                args=[service_revision.namespace, service_revision.name],
            ),
            data={"revision_tag": service_revision.tag},
        )

        self.assertEqual(
            response.json(),
            {
                "namespace": "my-org",
                "name": "my-service",
                "revision_tag": "1.0.0",
                "is_default": False,
            },
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
            {
                "namespace": namespace,
                "name": name,
                "revision_tag": latest_service_revision.tag,
                "is_default": False,
            },
        )

    def test_register_service_revision_without_revision_tag_causes_error_response(self):
        """Test that an error response is returned if attempting to register a service revision without providing a
        revision tag.
        """
        namespace = "octue"
        name = "new-service"
        response = self.client.post(
            reverse("service-revisions", kwargs={"namespace": namespace, "name": name}),
            data={},
            content_type="application/json",
        )

        self.assertEqual(
            response.json(),
            {"error": "A revision tag must be included when registering a new service revision"},
        )

    def test_register_service_revision(self):
        """Test registering a service revision works and returns a success response."""
        namespace = "octue"
        name = "new-service"
        revision_tag = "3.9.9"

        response = self.client.post(
            reverse("service-revisions", kwargs={"namespace": namespace, "name": name}),
            data={"revision_tag": revision_tag, "is_default": True},
            content_type="application/json",
        )

        self.assertEqual(response.json(), {})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ServiceRevision.objects.get(namespace=namespace, name=name, tag=revision_tag).is_default)
