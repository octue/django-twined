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
    """A mixin for the `Question` subclass providing helpers for retrieval of specific message kinds. These methods are
    backwards compatible with database entries created before the breaking change in version `0.7.0` was introduced,
    allowing the new and old formats of JSON data stored in the events to be accessed.
    """

    @property
    def delivery_acknowledgement(self):
        """Get the delivery acknowledgement for the question.

        :return django_twined.models.querysets.datastore_queryset.DatastoreQueryset:
        """
        try:
            return self.service_usage_events.get(self._get_event_filter("delivery_acknowledgement"))
        except ServiceUsageEvent.DoesNotExist:
            return None
        except ServiceUsageEvent.MultipleObjectsReturned:
            logger.warning(
                "MultipleObjectsReturned detected for delivery_acknowledgement ServiceUsageEvent on question %s",
                self.id,
            )
            return self.service_usage_events.filter(self._get_event_filter("delivery_acknowledgement")).first()

    @property
    def exceptions(self):
        """Get any exceptions raised by the child service during processing of the question.

        :return django_twined.models.querysets.datastore_queryset.DatastoreQueryset:
        """
        return self.service_usage_events.order_by("publish_time").filter(self._get_event_filter("exception")).all()

    @property
    def result(self):
        """Get the result produced by the child service in response to the question.

        :return django_twined.models.querysets.datastore_queryset.DatastoreQueryset:
        """
        try:
            return self.service_usage_events.get(self._get_event_filter("result"))
        except ServiceUsageEvent.DoesNotExist:
            return None
        except ServiceUsageEvent.MultipleObjectsReturned:
            logger.warning("MultipleObjectsReturned detected for result ServiceUsageEvent on question %s", self.id)
            return self.service_usage_events.filter(self._get_event_filter("result")).first()

    @property
    def log_records(self):
        """Get any log records produced by the child service processing the question.

        :return django_twined.models.querysets.datastore_queryset.DatastoreQueryset:
        """
        return self.service_usage_events.order_by("publish_time").filter(self._get_event_filter("log_record")).all()

    @property
    def monitor_messages(self):
        """Get any monitor messages produced by the child service processing the question.

        :return django_twined.models.querysets.datastore_queryset.DatastoreQueryset:
        """
        return (
            self.service_usage_events.order_by("publish_time").filter(self._get_event_filter("monitor_message")).all()
        )

    @property
    def latest_heartbeat(self):
        """Get the latest heartbeat of the child service processing the question.

        :return django_twined.models.querysets.datastore_queryset.DatastoreQueryset:
        """
        return self.service_usage_events.order_by("-publish_time").filter(self._get_event_filter("heartbeat")).first()

    def _get_event_filter(self, data_type_or_kind):
        """Get a filter for `ServiceUsageEvent` model instances that filters the JSON data of the `data` field for the
        given event kind using either the old `type` key or the new `kind` key. This maintains backwards compatibility
        with service usage events created before the breaking change in version `0.7.0` was introduced, allowing the new
        and old formats of the JSON data stored in the events to be accessed.

        :param str data_type_or_kind: the name of the event type/kind to filter for
        :return django.db.models.query_utils.Q:
        """
        return Q(data__type=data_type_or_kind) | Q(data__kind=data_type_or_kind)
