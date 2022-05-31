import json
import logging
from base64 import b64decode
from dateutil.parser import isoparse
from django.dispatch import receiver
from django_gcp.events.signals import event_received
from django_twined.models import QUESTION_ASKED, QUESTION_RESPONSE_UPDATED, ServiceUsageEvent


logger = logging.getLogger(__name__)


@receiver(event_received)
def receive_event(_, event_kind, event_reference, event_payload, event_parameters, **kwargs):
    """Handle question updates received from pubsub
    :param event_kind (str): A kind/variety allowing you to determine the handler to use (eg "something-update"). Required.
    :param event_reference (str): A reference value provided by the client allowing events to be sorted/filtered. Required.
    :param event_payload (dict, array): The event payload to process, already decoded.
    :param event_parameters (dict): Extra parameters passed to the endpoint using URL query parameters
    :return: None
    """

    if event_kind in (QUESTION_ASKED, QUESTION_RESPONSE_UPDATED):
        ServiceUsageEvent.objects.create(
            data=json.loads(b64decode(event_payload["data"])),
            kind=event_kind,
            publish_time=isoparse(event_payload["publishTime"]),
            question_id=event_reference,
            service_revision_id=event_parameters["srid"],
        )
