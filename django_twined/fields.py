import logging

from django.conf import settings
from django.db import models
from django.utils.module_loading import import_string


logger = logging.getLogger(__name__)


class DatafileObjectField(models.FileField):
    """A FileField allowing storage class to be declared in settings

    This enables storages to be switched without database migrations, and enables different FileFields to be associated
    with different storages rather than them all using the django media bucket.
    """

    def __init__(self, store_key=None, **kwargs):
        if store_key is None:
            raise ValueError(
                "Missing store_key argument. Your Datastore model must contain a `file = DatafileObjectField(store_key='...')` field declaration"
            )

        self.store_key = store_key
        store = settings.TWINED_DATA_STORES[store_key]
        kwargs["storage"] = import_string(store["storage"])(**store["storage_settings"])
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["store_key"] = self.store_key
        kwargs.pop("storage")
        return name, path, args, kwargs


class DatafileMetadataField(models.JSONField):
    """Contains metadata not otherwise present in"""

    def __init__(self, *args, **kwargs):
        kwargs["default"] = kwargs.pop("default", dict)
        kwargs["help_text"] = kwargs.pop("help_text", "Additional object metadata")
        super().__init__(*args, **kwargs)


class ValuesField(models.JSONField):
    """Values storage in the actual DB
    TODO accept schema for validation and render better forms
    """

    def __init__(self, *args, **kwargs):
        kwargs["default"] = kwargs.pop("default", dict)
        kwargs["help_text"] = kwargs.pop("help_text", "Values data")
        # By default, work around https://code.djangoproject.com/ticket/27697
        kwargs["blank"] = kwargs.pop("blank", True)
        super().__init__(*args, **kwargs)


class ManifestField(models.JSONField):
    """Manifest storage in the actual DB
    TODO accept schema for validation and render better forms
    """

    def __init__(self, *args, **kwargs):
        kwargs["default"] = kwargs.pop("default", dict)
        kwargs["help_text"] = kwargs.pop("help_text", "Manifest data")
        super().__init__(*args, **kwargs)
