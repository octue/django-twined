from django.db.models import CharField, DecimalField
from django_twined.fields import DatafileObjectField
from django_twined.models import AbstractSynchronisedDatastore


class ConcreteSynchronisedDatastore(AbstractSynchronisedDatastore):
    """
    This is how you test abstract classes in your library without adding concrete models: add the concrete model
     to your test app. You'll need to make the migrations for the test app:
       python manage.py makemigrations tests

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

        app_label = "tests"

    def __str__(self):
        # Ensures that the abstract class __str__ method is covered in testing
        return f"{super(ConcreteSynchronisedDatastore, self).__str__()} ('{self.a_string_tag}')"
