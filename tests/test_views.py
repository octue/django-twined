from unittest.mock import patch

from django.test.testcases import TestCase
from django.urls import reverse

from django_twined.models import ServiceRevision

NAMESPACE = "my-org"
NAME = "my-service"


class TestGetServiceRevision(TestCase):
    def test_invalid_http_method_causes_error_response(self):
        """Test that an error response is returned if using an invalid HTTP method with the endpoint."""
        response = self.client.patch(reverse("services", kwargs={"name": "some", "namespace": "service"}))
        self.assertEqual(response.json(), {"error": "Invalid request method."})

    def test_getting_nonexistent_service_revision_causes_error_response(self):
        """Test that an error response is returned if trying to get a non-existent service."""
        response = self.client.get(
            reverse("services", kwargs={"name": "non-existent", "namespace": "service"}),
            data={"revision_tag": "1.3.9"},
        )

        self.assertEqual(response.json(), {"error": "Service revision not found."})

    def test_get_service_revision_with_revision_tag(self):
        """Test getting a service revision when the revision tag is supplied."""
        service_revision = ServiceRevision.objects.create(namespace=NAMESPACE, name=NAME, tag="1.0.0")

        response = self.client.get(
            reverse("services", kwargs={"namespace": NAMESPACE, "name": NAME}),
            data={"revision_tag": service_revision.tag},
        )

        self.assertEqual(
            response.json(),
            {
                "namespace": NAMESPACE,
                "name": NAME,
                "revision_tag": "1.0.0",
                "is_default": False,
            },
        )

    def test_get_service_revision_without_revision_tag(self):
        """Test that the latest service revision is returned when the revision tag isn't supplied."""
        ServiceRevision.objects.create(namespace=NAMESPACE, name=NAME, tag="0.1.0")
        ServiceRevision.objects.create(namespace=NAMESPACE, name=NAME, tag="2.0.0")

        latest_service_revision = ServiceRevision.objects.create(
            namespace=NAMESPACE,
            name=NAME,
            tag="11.0.1",
            is_default=True,
        )

        response = self.client.get(reverse("services", kwargs={"namespace": NAMESPACE, "name": NAME}))

        self.assertEqual(
            response.json(),
            {
                "namespace": NAMESPACE,
                "name": NAME,
                "revision_tag": latest_service_revision.tag,
                "is_default": True,
            },
        )


class TestRegisterServiceRevision(TestCase):
    def test_register_service_revision_without_revision_tag_causes_error_response(self):
        """Test that an error response is returned if attempting to register a service revision without providing a
        revision tag.
        """
        response = self.client.post(
            reverse("services", kwargs={"namespace": NAMESPACE, "name": NAME}),
            data={},
            content_type="application/json",
        )

        self.assertEqual(
            response.json(),
            {"error": "A revision tag must be included when registering a new service revision."},
        )

    def test_register_service_revision(self):
        """Test registering a service revision works and returns a success response."""
        revision_tag = "3.9.9"

        response = self.client.post(
            reverse("services", kwargs={"namespace": NAMESPACE, "name": NAME}),
            data={"revision_tag": revision_tag},
            content_type="application/json",
        )

        self.assertEqual(response.json(), {})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ServiceRevision.objects.get(namespace=NAMESPACE, name=NAME, tag=revision_tag).is_default)

    def test_register_service_revision_with_is_default_specified_as_false(self):
        """Test that the `is_default` field is respected when registering a service revision when `is_default=False`,
        even when the `SERVICE_REVISION_IS_DEFAULT_CALLBACK` returns `True` for the revision.
        """
        revision_tag = "3.9.9"

        with patch("django_twined.views.SERVICE_REVISION_IS_DEFAULT_CALLBACK", return_value=True):
            response = self.client.post(
                reverse("services", kwargs={"namespace": NAMESPACE, "name": NAME}),
                data={"revision_tag": revision_tag, "is_default": False},
                content_type="application/json",
            )

        self.assertEqual(response.json(), {})
        self.assertEqual(response.status_code, 201)
        self.assertFalse(ServiceRevision.objects.get(namespace=NAMESPACE, name=NAME, tag=revision_tag).is_default)

    def test_register_service_revision_with_is_default_specified_as_true(self):
        """Test that the `is_default` field is respected when registering a service revision when `is_default=True`,
        even when the `SERVICE_REVISION_IS_DEFAULT_CALLBACK` returns `False` for the revision.
        """
        revision_tag = "3.9.9"

        with patch("django_twined.views.SERVICE_REVISION_IS_DEFAULT_CALLBACK", return_value=False):
            response = self.client.post(
                reverse("services", kwargs={"namespace": NAMESPACE, "name": NAME}),
                data={"revision_tag": revision_tag, "is_default": True},
                content_type="application/json",
            )

        self.assertEqual(response.json(), {})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(ServiceRevision.objects.get(namespace=NAMESPACE, name=NAME, tag=revision_tag).is_default)
