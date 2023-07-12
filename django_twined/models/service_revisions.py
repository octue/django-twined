import logging

import packaging.version
from django.conf import settings
from django.db import models, transaction
from django_gcp.events.utils import get_event_url
from octue.cloud.pub_sub.service import Service
from octue.cloud.service_id import convert_service_id_to_pub_sub_form
from octue.resources.service_backends import get_backend

from .service_usage_events import QUESTION_RESPONSE_UPDATED


logger = logging.getLogger(__name__)

QUESTION_ASK_TIMEOUT_SECONDS = 60


def service_revision_is_latest_semantic_version(service_revision):
    """Determine if a service revision is the latest semantic version based on its revision tag.

    :param django_twined.models.service_revision.ServiceRevision service_revision: the service revision to check
    :return bool: `True` if the service revision is the latest semantic version according to its revision tag
    """
    sorted_service_revisions = sorted(
        [
            *ServiceRevision.objects.filter(namespace=service_revision.namespace, name=service_revision.name),
            service_revision,
        ],
        key=lambda revision: packaging.version.parse(revision.tag),
    )

    return sorted_service_revisions[-1] == service_revision


def get_default_namespace():
    """Return the default namespace for service revisions"""
    return settings.TWINED_DEFAULT_NAMESPACE


def get_default_project_name():
    """Return the default project name for service revisions"""
    return settings.TWINED_DEFAULT_PROJECT_NAME


def get_default_tag():
    """Return the default tag if set, otherwise 'latest'"""
    return getattr(settings, "TWINED_DEFAULT_TAG", "latest")


class AbstractServiceRevision(models.Model):
    """Abstract model to register available services in the system"""

    id = models.BigAutoField(primary_key=True, editable=False)

    is_default = models.BooleanField(
        default=False,
        help_text="Set true to use this tagged revision as the default version for this name and namespace",
    )

    created = models.DateTimeField(
        auto_now_add=True, help_text="When this service revision was created (or, strictly, added to this db)"
    )

    namespace = models.SlugField(
        max_length=80,
        default=get_default_namespace,
        blank=False,
        null=False,
        help_text="The organisation namespace, eg 'octue'",
    )

    name = models.SlugField(
        help_text="The name of the service eg 'example-service'",
    )

    tag = models.CharField(
        max_length=80,
        default=get_default_tag,
        blank=False,
        null=False,
        help_text="The service revision tag that helps to identify the unique deployment",
    )

    # GCP provider-specific - will become more flexible over time.
    project_name = models.CharField(
        max_length=80,
        default=get_default_project_name,
        help_text="The name of the GCP project in which the service resides",
    )

    class Meta:
        """Metaclass for AbstractServiceRevision"""

        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["namespace", "name", "tag"],
                name="unique_identifier",
            ),
        ]

    @property
    def sruid(self):
        """Return the Service Revision Unique Identifier

        Comprises the namespace, name, version, and tag parameters that together uniquely identify a revision (e.g. for
        the purposes of addressing).

        Using docker image labeling as inspiration, this looks like octue/example-service:0.1.2 or
        octue/example-service:my-branch or octue/example-service:0.1.2-r1 enabling both routing to specific revisions
        and things like branches for review.
        """
        return f"{self.namespace}/{self.name}:{self.tag}"

    @property
    def topic(self):
        """Return the octue GCP topic address string.

        :return str:
        """
        return "octue.services." + convert_service_id_to_pub_sub_form(self.sruid)

    def ask(
        self,
        question_id,
        input_values=None,
        input_manifest=None,
        push_url=None,
        asker_name="django-twined",
        **kwargs,
    ):
        """Ask a question of this service revision

        Asks the question and registers a push subscription, to deliver response events on the
        question topic to an endpoint.
        :param Union[str, uuid.UUID] question_id: A uuid to refer to the question by
        :param Union[dict, None] input_values: The input values of the question
        :param Union[octue.Manifest, None] input_manifest: The input manifest of the question
        :param Union[str, None] push_url: Absolute URL to the endpoint where answers and updates should be pushed (by default this is generated using django-gcp, modifying this value will require you to provide a view and full message handling at the endpoint)
        :param str asker_name: A name for this 'root service' that's asking the question.

        ```
        ServiceRevision.objects.get(
            namespace="octue",
            name="my-service",
            tag="latest"
        ).ask(
            question_id='some-uuid',
            input_values={},
            input_manifest=Manifest()
        )
        ```

        """
        if push_url is None:
            push_url = get_event_url(
                event_kind=QUESTION_RESPONSE_UPDATED,
                event_reference=question_id,
                event_parameters={
                    "srid": self.id,  # Adding this (internal) ForeignKey enables creation of ServiceUsageEvents in one DB roundtrip, not two.
                    "sruid": self.sruid,
                },
                base_url=settings.TWINED_BASE_URL,
            )

        backend = get_backend()(project_name=self.project_name)
        asker = Service(backend=backend, name=asker_name)

        subscription, _ = asker.ask(
            service_id=self.sruid,
            question_uuid=str(question_id),
            input_values=input_values,
            input_manifest=input_manifest,
            push_endpoint=push_url,
            timeout=QUESTION_ASK_TIMEOUT_SECONDS,
            **kwargs,
        )

        return subscription, push_url

    def __str__(self):
        return self.sruid

    def __repr__(self):
        return f"Service Revision ({self.sruid})"

    def save(self, *args, **kwargs):
        """Override save method to ensure that there can be only one default service revision."""
        with transaction.atomic():
            if self.is_default:
                previous_default = ServiceRevision.objects.filter(
                    namespace=self.namespace,
                    name=self.name,
                    is_default=True,
                ).first()

                if previous_default is not None:
                    previous_default.is_default = False
                    previous_default.save()

            super().save(*args, **kwargs)


class ServiceRevision(AbstractServiceRevision):
    """Concrete model to register available service revisions in the system"""


def get_default_service_revision(namespace, name):
    """Get a default service revision to use given a namespace/name combination

    Uses the is_default property of ServiceRevisions to determine which revision should be used in the absence of a specific tag

    :param str namespace: The namespace within which the default resides
    :param str name: The name for which the default revision will be returned
    :return Union[ServiceRevision | None]: The default service revision to use, or None if there isn't one

    """

    return ServiceRevision.objects.filter(name=name, namespace=namespace, is_default=True).first()
