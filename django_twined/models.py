import logging
from django.db import models
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


class AbstractModel(models.Model):
    slug = models.SlugField(
        verbose_name=_("slug"), allow_unicode=False, unique=True, max_length=255, help_text=_("A slug.")
    )

    class Meta:
        abstract = True


class MyModel(AbstractModel):
    """
    This is how you test abstract classes in your library without adding concrete models: add the concrete model
     to your test app. You'll need to make the migrations for the test app:
       python manage.py makemigrations tests

    """

    name = models.CharField(max_length=32)

    class Meta:
        app_label = "tests"

    def __str__(self):
        # Ensures that the abstract class __str__ method is covered in testing
        return super(MyModel, self).__str__() + ' ("{}")'.format(self.name)
