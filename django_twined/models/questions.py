import logging
import uuid
from datetime import datetime, timezone
from django.db import models
from model_utils.managers import InheritanceManager

from ..fields import ManifestField, ValuesField


logger = logging.getLogger(__name__)


class AbstractQuestion(models.Model):
    """Abstract Base Class for a Question model to store questions asked to octue services"""

    duplicate_fields = ()

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    asked = models.DateTimeField(null=True, blank=True, editable=False, help_text="When the question was asked")
    answered = models.DateTimeField(null=True, blank=True, editable=False, help_text="When the question was answered")

    class Meta:
        """Metaclass for AbstractQuestion"""

        abstract = True

    objects = InheritanceManager()

    def __str__(self):
        return f"{self.id}"

    def __repr__(self):
        return f"{self.__class__.__name__} ({self.id})"

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


class Question(AbstractQuestion):
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

    def get_service_revision(self):
        return self.service_revision


class QuestionValuesDatabaseStorageMixin:
    """DEPRECATED - DO NOT USE
    Use this mixin to store question-and-answer values data in the actual database

    This will be deprecated as we move to using an event store for question asks and updates,
    to avoid duplicates.

    Instead, override the get_input_values() and get_output_values() methods to access
    the event store.
    """

    input_values = ValuesField(help_text="Contents of the input_values strand")

    output_values = ValuesField(help_text="Contents of the output_values strand")

    def get_input_values(self):
        """Override the get_input_values abstract class method to return the values from the database store"""
        return self.input_values

    def get_output_values(self):
        """Override the get_output_values abstract class method to return the values from the database store"""
        return self.output_values


class QuestionManifestsDatabaseStorageMixin:
    """DEPRECATED - DO NOT USE
    Use this mixin to store question-and-answer manifest data in the actual database.

    This will be deprecated as we move to event based processing, to avoid duplicates. Do not change!
    Instead, use ManyToManyFields to <Subclass>DataStore in your <Subclass>Question, and override
    the get_input_manifest() and get_output_manifest() methods.
    """

    input_manifest = ManifestField(help_text="Contents of the input_manifest strand")

    output_manifest = ManifestField(help_text="Contents of the output_manifest strand")

    def get_input_manifest(self):
        """Override the get_input_manifest abstract class method to return the manifest from the database store"""
        return self.input_manifest

    def get_output_manifest(self):
        """Override the get_output_manifest abstract class method to return the manifest from the database store"""
        return self.output_manifest
