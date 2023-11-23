import logging

from django.dispatch import receiver
from django_gcp.events.signals import event_received
from django_gcp.events.utils import decode_pubsub_message
from django_twined.models import QUESTION_ASKED, QUESTION_RESPONSE_UPDATED, ServiceUsageEvent
from django_twined.signals.senders import (
    delivery_acknowledgement_received,
    exception_received,
    heartbeat_received,
    log_record_received,
    monitor_message_received,
    question_asked,
    result_received,
)


logger = logging.getLogger(__name__)


@receiver(event_received)
def receive_event(sender, event_kind, event_reference, event_payload, event_parameters, **kwargs):
    """Handle question updates received from pubsub
    :param event_kind (str): A kind/variety allowing you to determine the handler to use (eg "something-update"). Required.
    :param event_reference (str): A reference value provided by the client allowing events to be sorted/filtered. Required.
    :param event_payload (dict, array): The event payload to process, already decoded.
    :param event_parameters (dict): Extra parameters passed to the endpoint using URL query parameters
    :return: None
    """

    if event_kind in (QUESTION_ASKED, QUESTION_RESPONSE_UPDATED):
        decoded = decode_pubsub_message(event_payload)

        logger.debug(
            "Storing ServiceUsageEvent from event_kind %s, event_reference %s, from sender %s - PubSub message_id %s, ordering_key %s, publish_time %s, subscription %s",
            event_kind,
            event_reference,
            sender,
            decoded["message_id"],
            decoded["ordering_key"],
            decoded["publish_time"],
            decoded["subscription"],
        )

        sue = ServiceUsageEvent.objects.create(
            data=decoded["data"],
            kind=event_kind,
            publish_time=decoded["publish_time"],
            question_id=event_reference,
            service_revision_id=event_parameters["srid"],
        )

        event_kind = decoded["data"].get("kind", None)

        if event_kind == "delivery_acknowledgement":
            delivery_acknowledgement_received.send(sender=ServiceUsageEvent, service_usage_event=sue)

        if event_kind == "exception":
            exception_received.send(sender=ServiceUsageEvent, service_usage_event=sue)

        elif event_kind == "heartbeat":
            heartbeat_received.send(sender=ServiceUsageEvent, service_usage_event=sue)

        elif event_kind == "log_record":
            log_record_received.send(sender=ServiceUsageEvent, service_usage_event=sue)

        elif event_kind == "monitor_message":
            monitor_message_received.send(sender=ServiceUsageEvent, service_usage_event=sue)

        elif event_kind == "result":
            result_received.send(sender=ServiceUsageEvent, service_usage_event=sue)

        elif event_kind == QUESTION_ASKED:
            question_asked.send(sender=ServiceUsageEvent, service_usage_event=sue)

        else:
            logger.warning("Unknown event kind: (%s) for ServiceUsageEvent %s", event_kind, sue.id)
