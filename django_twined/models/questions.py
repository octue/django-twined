import logging
import uuid
from datetime import datetime, timezone

from django.db import models
from django_twined.models.service_usage_events import QuestionEventsMixin
from model_utils.managers import InheritanceManager


logger = logging.getLogger(__name__)


NO_STATUS = -100
BAD_INPUT_STATUS = -3
TIMEOUT_STATUS = -2
ERROR_STATUS = -1
IN_PROGRESS_STATUS = 0
SUCCESS_STATUS = 1

STATUS_MESSAGE_MAP = {
    NO_STATUS: "No status",
    BAD_INPUT_STATUS: "Failed (invalid inputs)",
    TIMEOUT_STATUS: "Failed (timeout)",
    ERROR_STATUS: "Failed (error)",
    IN_PROGRESS_STATUS: "In progress",
    SUCCESS_STATUS: "Complete",
}

STATUS_CHOICES = tuple((k, v) for k, v in STATUS_MESSAGE_MAP.items())


class AbstractQuestion(models.Model):
    """Abstract Base Class for a Question model to store questions asked to octue services"""

    duplicate_fields = ()

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    asked = models.DateTimeField(null=True, blank=True, editable=False, help_text="When the question was asked")
    answered = models.DateTimeField(null=True, blank=True, editable=False, help_text="When the question was answered")
    status = models.IntegerField(default=-100, choices=STATUS_CHOICES)

    class Meta:
        """Metaclass for AbstractQuestion"""

        abstract = True

    objects = InheritanceManager()

    def __str__(self):
        return f"{self.id}"

    def __repr__(self):
        return f"{self.__class__.__name__} ({self.id})"

    @property
    def status_message(self):
        """Short verbose (human-readable, for display) text indicating status of the question.

        :return str:
        """
        return STATUS_MESSAGE_MAP[self.status]

    def get_duplicate(self, save=True):
        """Duplicate the question instance and optionally save to the database"""
        kwargs = {}
        for field in self.duplicate_fields:
            kwargs[field] = getattr(self, field)
        # Always override the asked and answered attributes of the duplicate
        overrides = {"asked": None, "answered": None}
        duplicate = self.__class__(**kwargs, **overrides)
        if save:
            duplicate.save()
        return duplicate

    def get_input_values(self):
        """Get the input values from wherever they're stored (or compute them)
        This method must be overriden in subclasses of Question
        """
        raise NotImplementedError(
            "You must override the get_input_values method for this class (or provide input directly to ask() method)"
        )

    def get_input_manifest(self):
        """Get the input manifest from wherever it's stored (or compute it)
        This method must be overriden in subclasses of Question
        """
        raise NotImplementedError(
            "You must override the get_input_manifest method for this class (or provide input directly to ask() method)"
        )

    def get_output_values(self):
        """Get the output values from wherever they're stored (or compute them) This method must be overriden in
        subclasses of Question.
        """
        raise NotImplementedError(
            "You must override the get_input_values method for this class (or provide input directly to ask() method)"
        )

    def get_output_manifest(self):
        """Get the output manifest from wherever it's stored (or compute it). This method must be overriden in
        subclasses of Question.
        """
        raise NotImplementedError(
            "You must override the get_input_manifest method for this class (or provide input directly to ask() method)"
        )

    def get_service_revision(self):
        """Get the service revision from wherever it's stored (or otherwise determine it)
        This method must be overriden in subclasses of Question
        """
        raise NotImplementedError(
            "You must override the get_service_revision method for this class (or provide input directly to ask() method)"
        )

    def as_subclass(self):
        """Returns a base question object as its inherited subclass"""
        return self.__class__.objects.get_subclass(id=self.id)

    def ask(self, save=True):
        """Ask a question to a service_revision.

        :param boolean save: If true, this question will be saved in order to update the 'asked' time.
        """

        service_revision = self.get_service_revision()
        subscription, push_url = service_revision.ask(
            question_id=self.id,
            input_values=self.get_input_values(),
            input_manifest=self.get_input_manifest(),
        )

        logger.info("Service Revision %s was asked question %s", service_revision.sruid, self.id)

        self.asked = datetime.now().replace(tzinfo=timezone.utc)

        if save:
            self.save()

        return subscription, push_url, service_revision


class Question(AbstractQuestion, QuestionEventsMixin):
    """Stores questions asked to octue services

    This concrete model is here to link questions to the service revisions
    used to ask them. It is intended to be subclassed for specific question types,
    hence why it doesn't override the getters for input and output values.

    """

    service_revision = models.ForeignKey(
        "django_twined.ServiceRevision",
        blank=True,
        null=True,
        related_name="questions",
        on_delete=models.PROTECT,
    )

    def get_service_revision(self):
        return self.service_revision
