# Disables for testing:
# pylint: disable=missing-docstring

from datetime import datetime
from unittest.mock import patch

from django.test import TestCase
from django_gcp.events.utils import make_pubsub_message
from django_twined.models import QUESTION_RESPONSE_UPDATED, ServiceRevision, ServiceUsageEvent

from tests.server.example.models import QuestionWithValuesDatabaseStorage


# TODO test the following
# from django_twined.models import (
#     # QUESTION_ASKED,
#     # QUESTION_STATUS_UPDATED,
# )
# from django_twined.signals import receive_event


class MockService:
    """A mock octue Service that can send and receive messages"""

    def __init__(self, *args, **kwargs):
        pass

    def ask(self, *args, **kwargs):
        # Not the correct type but whatever, we don't care here
        return ("subscription", "b")


class ServiceUsageEventTestCase(TestCase):
    def _setup_to_receive_events(self):
        """Use a patched octue Service to avoid need for credentials"""

        with patch("django_twined.models.service_revisions.Service", new=MockService) as mock:

            mock.return_value = ("subscription", "push_url")

            sr = ServiceRevision.objects.create(
                project_name="gargantuan-gibbons", namespace="large-gibbons", name="gibbon-analyser", tag="1.0.0"
            )

            q = QuestionWithValuesDatabaseStorage.objects.create(service_revision=sr)
            _, push_url, _ = q.ask()

            return sr, q, push_url

    def test_event_handler(self):
        """Ensure that a different kind of event is passed on silently"""
        sr, q, push_url = self._setup_to_receive_events()

        self.assertTrue(
            push_url.startswith(f"https://my-server.com/gcp/events/{QUESTION_RESPONSE_UPDATED}/{str(q.id)}")
        )
        self.assertTrue("sruid=large-gibbons%2Fgibbon-analyser%3A1.0.0" in push_url)
        self.assertTrue(f"srid={str(sr.id)}" in push_url)

        local_url = push_url.replace("https://my-server.com", "")

        msg_data = {"the-event": "payload"}
        msg_subscription = "projects/my-project/subscriptions/my-subscription-name"
        msg = make_pubsub_message(msg_data, msg_subscription, publish_time=datetime.now())

        response = self.client.post(
            local_url,
            data=msg,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

        self.assertEqual(ServiceUsageEvent.objects.count(), 1)
