import logging
from django.db import models
from django.utils.translation import ugettext_lazy as _


logger = logging.getLogger(__name__)


class AbstractModel(models.Model):
    slug = models.SlugField(
        verbose_name=_("slug"), allow_unicode=False, unique=True, max_length=255, help_text=_("A slug.")
    )

    class Meta:
        abstract = True
