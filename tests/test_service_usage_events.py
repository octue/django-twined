# Disables for testing:
# pylint: disable=missing-docstring

import uuid
from datetime import datetime
from unittest.mock import patch
from django.test import TestCase
from django_twined.models import QUESTION_RESPONSE_UPDATED, ServiceRevision, ServiceUsageEvent

from tests.server.example.models import QuestionWithValuesDatabaseStorage
from .make_pubsub_message import make_pubsub_message


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
                topic_id=uuid.uuid4(),
                name="gibbon-analyser",
            )

            q = QuestionWithValuesDatabaseStorage.objects.create(service_revision=sr)
            _, push_url = q.ask()

            return sr, q, push_url

    def test_event_handler_signal_is_called(self):
        """"""

    def test_event_handler(self):
        """Ensure that a different kind of event is passed on silently"""
        sr, q, push_url = self._setup_to_receive_events()

        self.assertTrue(
            push_url.startswith(f"https://my-server.com/gcp/events/{QUESTION_RESPONSE_UPDATED}/{str(q.id)}")
        )
        self.assertTrue("sruid=test-default-namespace%2Fgibbon-analyser%3Atest-default-tag" in push_url)
        self.assertTrue(f"srid={str(sr.id)}" in push_url)

        local_url = push_url.replace("https://my-server.com", "")

        msg = make_pubsub_message(data={"the-event": "payload"}, publish_time=datetime.now())

        response = self.client.post(
            local_url,
            data=msg,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

        self.assertEqual(ServiceUsageEvent.objects.count(), 1)
