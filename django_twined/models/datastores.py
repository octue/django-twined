import json
import logging
import uuid
from django.db import models
from octue.resources import Datafile
from octue.utils.encoders import OctueJSONEncoder

from .querysets import DatastoreQueryset


logger = logging.getLogger(__name__)


class AbstractSynchronisedDatastore(models.Model):
    """Rows in the database correspond to files in an object store, with metadata synchronized for search/querying

    The most obvious question is:
        *"Why don't I just keep the metadata in the DB table and the object in the store, like normal?"*

    Some good answers:
        - because that separates the file objects and their metadata
        - because interaction with the database is then required by every service that wants to use the data, which
            - limits scalability of the system
            - requires the dba / backend team to weigh in heavily on every application that uses or creates data
            - precludes creation of data by untrusted or third party services
            - requires the dba / backend team to design and/or have deep knowledge of the intrinsic data type contained
              in the files in order to design appropriate and consistent metadata for them

    Yes, sync to a database like this is a duplication of the metadata and that requires an additional job to maintain
    consistency, which is a pain to maintain that one synchronisation system, but not an unscalable activity.

    You can think of this like you'd think about search indexes. In order to make data items searchable you'd include
    them in a search index, which is a duplicate of metadata. Here, we're duplicating metadata in order to make our data
    items queryable, relatable to other entities AND searchable (with postgres full text search, or solutions like
    ZomboDB or django-haystack to integrate elasticsearch).

    Of course you can also use your own business logic/auth and permission systems like django guardian to control
    access and visibility of your data items however you want.

    """

    __TAG_FIELDS__ = set()
    __FILE_FIELD__ = "file"

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)

    objects = DatastoreQueryset.as_manager()

    class Meta:
        abstract = True

    @property
    def project_name(self):
        return self._storage.project_id

    @property
    def datafile(self):
        """The octue datafile associated with this instance"""

        if self._state.adding:
            # TODO Once https://github.com/octue/octue-sdk-python/issues/200 is resolved, we will be able to
            # Retun datafiles from the cloud prior to calling () save on a new instantiated model.
            return None

        # Handle event of instance has unset file or file not yet in store
        if self._location is None:
            raise ValueError("Instance has no file field set, cannot create Datafile")

        return Datafile(self.gs_path, project_name=self._storage.project_id)

    @classmethod
    def from_datafile(cls, datafile, create_if_missing=True, update_db_metadata=True):
        """Gets database record corresponding to an octue datafile object.

        The returned instance is always updated with metadata from the datafile object, however, this updated
        instance will only be saved to the database if update_db_metadata is true, so it is possible to return a dirty
        instance from this method.

        :param datafile: Datafile object representing a cloud or local file and its metadata
        :type datafile: octue.Datafile
        :param create_if_missing: Create a database entry for this file and its metadata if it's not present
        :type create_if_missing: bool
        :param update_db_metadata: If database entry for this file is found, ensure the metadata in that row is up to date with metadata from the cloud store
        :type update_db_metadata: bool
        :return: Instance of db model
        :rtype: AbstractSynchronisedDatastore
        """

        created = False
        try:
            instance = cls.objects.get(id=datafile.id)
            if update_db_metadata:
                instance.update_instance_from_tags(datafile.tags)
                instance.update_instance_from_labels(datafile.labels)
                instance.save()

        except cls.DoesNotExist:
            instance = cls(id=datafile.id)
            instance.update_instance_from_tags(datafile.tags)
            instance.update_instance_from_labels(datafile.labels)

            # TODO see https://github.com/octue/octue-sdk-python/issues/204 - once closed, a better way of doing this will be accessible
            if datafile.path.startswith("gs://"):
                path_in_bucket = datafile.path.replace("gs://", "").split("/", 1)[1]
            else:
                path_in_bucket = datafile.path.lstrip("/")

            # Set the file field .name attribute directly to path (https://stackoverflow.com/a/10906037/3556110)
            getattr(instance, cls.__FILE_FIELD__).name = path_in_bucket

            if create_if_missing:
                instance.save()
                created = True

        return instance, created

    def get_tags_from_instance(self):
        """Get tags (a dict of key-value pairs) from this instance

        Override this method to customise how Datafile tags are created from model instance fields (or other data)
        """
        tags = dict((name, getattr(self, name)) for name in self.__TAG_FIELDS__)

        # TODO A ***FAR*** LESS TERRIBLE SERIALIZER THAN THIS BASED ON AVRO OR SIMILAR!!!
        for k, v in tags.items():
            if v.__class__.__name__ == "Decimal":
                tags[k] = float(v)

        return tags

    def get_labels_from_instance(self):
        """Get labels as a set of strings from this instance

        Override this method to customise how Datafile labels are created from the instance fields (or other data)
        """
        return set()

    def update_instance_from_tags(self, tags):
        """Set this instance's fields using provided tags (a dict or TagDict of key-value pairs)

        Override this method to customise how metadata gets updated to the model instance (from the Datafile)
        """
        for name in self.__TAG_FIELDS__:
            setattr(self, name, tags.get(name, None))

    def update_instance_from_labels(self, labels=None):
        """Update this instance's fields using provided labels (a set of strings)

        Override this method to customise how metadata gets updated to the model instance (from the Datafile)
        """
        pass

    @property
    def _file_field(self):
        return getattr(self, self.__FILE_FIELD__)

    @property
    def _storage(self):
        return self.get_storage()

    @property
    def _storage_settings(self):
        return self.get_storage_settings()

    @classmethod
    def get_storage(cls):
        mapped_fields = dict((field.attname, field) for field in cls._meta.concrete_fields)
        return mapped_fields[cls.__FILE_FIELD__].storage

    @classmethod
    def get_storage_settings(cls):
        mapped_fields = dict((field.attname, field) for field in cls._meta.concrete_fields)
        return mapped_fields[cls.__FILE_FIELD__].store["storage_settings"]

    @property
    def _location(self):
        if self._storage.location != "":
            return self._storage.location
        elif self._file_field.name != "":
            return self._file_field.name
        else:
            return None

    @property
    def gs_path(self):
        return f"gs://{self._storage.bucket_name}/{self._location}"

    def _todo_expose_on_sdk(self, metadata):
        """Encode metadata as a dictionary of JSON strings."""
        if not isinstance(metadata, dict):
            raise TypeError(f"Metadata for Google Cloud storage should be a dictionary; received {metadata!r}")

        return {key: json.dumps(value, cls=OctueJSONEncoder) for key, value in metadata.items()}

    def save(self, *args, **kwargs):
        """Override the save method to synchronize metadata to the cloud store"""

        # Create a hypothetical (doesn't care if it's remote or local, or never existing)
        #  datafile instance simply to generate octue-compliant metadata
        datafile = Datafile(
            self._location,
            id=self.id,
            tags=self.get_tags_from_instance(),
            labels=self.get_labels_from_instance(),
            hypothetical=True,
        )
        metadata = self._todo_expose_on_sdk(datafile.metadata())

        # Only commit to saving if saving the metadata works correctly too
        self.file.file.metadata = metadata
        super().save(*args, **kwargs)

        # Update the metadata that we added (id, tags, labels) above
        datafile = self.datafile
        datafile.tags = self.get_tags_from_instance()
        datafile.labels = self.get_labels_from_instance()
        datafile.update_cloud_metadata()
