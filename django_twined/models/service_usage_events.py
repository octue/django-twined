import logging
from django.db import models


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
        max_length=20, null=False, blank=False, help_text="Event kind", choices=SERVICE_USAGE_EVENT_KINDS_CHOICES
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
