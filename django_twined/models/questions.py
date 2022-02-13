import logging
import uuid
from django.db import models

from ..fields import ManifestField, ValuesField


logger = logging.getLogger(__name__)


class AbstractQuestion(models.Model):

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    asked = models.DateTimeField(null=True, blank=True, help_text="When the question was asked")
    answered = models.DateTimeField(null=True, blank=True, help_text="When the question was answered")

    class Meta:
        abstract = True


class Question(AbstractQuestion):
    registered_service = models.ForeignKey(
        "django_twined.RegisteredService",
        related_name="questions",
        on_delete=models.PROTECT,
    )


class QuestionValuesDatabaseStorageMixin:
    """Use this mixin to store question-and-answer values data in the actual database"""

    input_values = ValuesField(help_text="Contents of the input_values strand")

    output_values = ValuesField(help_text="Contents of the output_values strand")


class QuestionManifestsDatabaseStorageMixin:
    """Use this mixin to store question-and-answer manifest data in the actual database"""

    input_manifest = ManifestField(help_text="Contents of the input_manifest strand")

    output_manifest = ManifestField(help_text="Contents of the output_manifest strand")
