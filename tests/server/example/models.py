# Disable (the mixin overrides the abstract methods)
# pylint: disable=abstract-method

from django.db.models import CharField, DecimalField
from django_twined.fields import DatafileObjectField
from django_twined.models import AbstractSynchronisedDatastore, Question, QuestionValuesDatabaseStorageMixin


# from model_utils.managers import InheritanceManager


class ConcreteSynchronisedDatastore(AbstractSynchronisedDatastore):
    """
    A Concrete Synchronised Datastore model for testing
    """

    a_string_tag = CharField(help_text="A string tag", null=False, blank=True, max_length=32)

    a_decimal_tag = DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text="A decimal number tag",
        null=False,
        blank=False,
    )

    __TAG_FIELDS__ = {
        "a_string_tag",
        "a_decimal_tag",
    }

    file = DatafileObjectField(
        store_key="django-twined-concrete-store",
        help_text="Upload a data file which will have Octue metadata on it",
    )

    class Meta:
        """Metaclass for the test app model"""

        app_label = "example"

    def __str__(self):
        # Ensures that the abstract class __str__ method is covered in testing
        return f"{super(ConcreteSynchronisedDatastore, self).__str__()} ('{self.a_string_tag}')"


class QuestionWithValuesDatabaseStorage(QuestionValuesDatabaseStorageMixin, Question):
    """
    A Question subclass with implemented input values for testing
    """

    # objects = InheritanceManager()

    class Meta:
        """Metaclass for the test app model"""

        app_label = "example"

    def get_input_manifest(self):
        """Not testing with manifests for now (better solution required)"""
        return None

    def get_output_manifest(self):
        """Not testing with manifests for now (better solution than DB storage required)"""
        return None
