import logging

from django.db import models
from django.db.models import Q


logger = logging.getLogger(__name__)


QUESTION_ASKED = "q-asked"
QUESTION_RESPONSE_UPDATED = "q-response-updated"
QUESTION_STATUS_UPDATED = "q-status-updated"

SERVICE_USAGE_EVENT_KINDS = {
    QUESTION_ASKED: "Question asked",
    QUESTION_RESPONSE_UPDATED: "Question response updated",
    QUESTION_STATUS_UPDATED: "Question status updated",
}

SERVICE_USAGE_EVENT_KINDS_CHOICES = tuple((k, v) for k, v in SERVICE_USAGE_EVENT_KINDS.items())


class AbstractEvent(models.Model):
    """Abstract base model for storing events

    This allows creation of multiple different tables for storage of different events.

    """

    id = models.BigAutoField(primary_key=True)

    data = models.JSONField(blank=False, null=False, editable=False, help_text="Event payload")

    kind = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        help_text="Event kind",
        choices=SERVICE_USAGE_EVENT_KINDS_CHOICES,
    )

    publish_time = models.DateTimeField(null=False, blank=False, help_text="Event timestamp")

    class Meta:
        """AbstractEvent meta class data"""

        abstract = True


class ServiceUsageEvent(AbstractEvent):
    """Table for storing Service Usage Events

    This table will store events related to usage of octue services (for example, question asks, answers, updates and responses)
    in your main database.

    For high volume processing, you may wish not to store events at all, or you may wish to store in a different
    database such as BigQuery. More helper tools for this coming soon.

    This table relates to concrete Question and Service Revision models. Null relations are
    not allowed, meaning that the table cannot store events not generated with django-twined
    (i.e. where Service Revision and Question models do not exist). This may change in future,
    to enable absorption of questions triggered by other services.
    """

    question = models.ForeignKey(
        "django_twined.Question",
        null=False,
        blank=False,
        related_name="service_usage_events",
        on_delete=models.CASCADE,
        editable=False,
    )

    service_revision = models.ForeignKey(
        "django_twined.ServiceRevision",
        null=False,
        blank=False,
        related_name="service_usage_events",
        on_delete=models.PROTECT,
        editable=False,
    )

    def __str__(self):
        return str(self.kind)

    def __repr__(self):
        return f"Service Usage Event {self.kind}"


class QuestionEventsMixin:
    """A mixin for Question subclass providing helpers for retrieval of specific message kinds"""

    @property
    def delivery_acknowledgement(self):
        try:
            return self.service_usage_events.get(
                Q(data__type="delivery_acknowledgement") | Q(data__kind="delivery_acknowledgement")
            )
        except ServiceUsageEvent.DoesNotExist:
            return None
        except ServiceUsageEvent.MultipleObjectsReturned:
            logger.warning(
                "MultipleObjectsReturned detected for delivery_acknowledgement ServiceUsageEvent on question %s",
                self.id,
            )
            return self.service_usage_events.filter(
                Q(data__type="delivery_acknowledgement") | Q(data__kind="delivery_acknowledgement")
            ).first()

    @property
    def exceptions(self):
        return (
            self.service_usage_events.order_by("publish_time")
            .filter(Q(data__type="exception") | Q(data__kind="exception"))
            .all()
        )

    @property
    def result(self):
        try:
            return self.service_usage_events.get(Q(data__type="result") | Q(data__kind="result"))
        except ServiceUsageEvent.DoesNotExist:
            return None
        except ServiceUsageEvent.MultipleObjectsReturned:
            logger.warning(
                "MultipleObjectsReturned detected for result ServiceUsageEvent on question %s",
                self.id,
            )
            return self.service_usage_events.filter(Q(data__type="result") | Q(data__kind="result")).first()

    @property
    def log_records(self):
        return (
            self.service_usage_events.order_by("publish_time")
            .filter(Q(data__type="log_record") | Q(data__kind="log_record"))
            .all()
        )

    @property
    def monitor_messages(self):
        return (
            self.service_usage_events.order_by("publish_time")
            .filter(Q(data__type="monitor_message") | Q(data__kind="monitor_message"))
            .all()
        )

    @property
    def latest_heartbeat(self):
        return (
            self.service_usage_events.order_by("-publish_time")
            .filter(Q(data__type="heartbeat") | Q(data__kind="heartbeat"))
            .first()
        )
