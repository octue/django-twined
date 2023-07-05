import json
import logging
import uuid
import warnings

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
        warnings.warn(
            "'project_name' property accessed on datastore object. This shouldn't be used and instead accessed directly from the storage class",
            DeprecationWarning,
        )

        return self._storage.project_id

    @property
    def datafile(self):
        """This instance as an octue datafile, constructed without accessing the store

        The metadata on this file is set from the instance, NOT from the store, so may not be fresh.

        Use `to_datafile(update_from_store=True) to ensure metadata on the datafile is fresh, although this will involve
        a call to the store so will take a long time for many datafiles.

        """
        return self.to_datafile(update_from_store=False)

    def to_datafile(self, update_from_store=True, allow_no_location=False):
        """Create an octue datafile instance corresponding to this datastore instance
        :param bool update_from_store: Fetch the latest metadata from the store. This can be an expensive operation because
        it requires an API call to the store; but is set default True to ensure that metadata reutrned is always fresh.
        Set this value to false to instead populate metadata directly from the instance, resulting in a much quicker operation.
        Generally the best approach is to set this value to false, and put in place a process to ensure your metadata is
        correctly synced from the datalake files.
        :param bool allow_no_location: Allow creation of a datafile even if the instance has no field file value set. This
        can happen on instance creation (e.g. if a data blob is being used to create an object, and therefore doesn't have a name).
        In this case, the datafile itself will be useless in the sense that data cannot be retrieved, but creating it allows
        manipulation of metadata in a way consistent with a datafile. The main use of this is to allow creation of octue metadata
        before a file is in the store, allowing use of custom storage but providing metadata on creation of the object to prevent
        repeated calls.

        :return octue.Datafile:
        """

        # Handle event of instance has unset file or file not yet in store
        if self._location is None:
            if allow_no_location:
                path = "unknown"
            else:
                raise ValueError(
                    "Instance has no file field set, cannot create Datafile. Try saving the instance first, or if you're operating on an unsaved instance see the `allow_no_location` option."
                )

        else:
            path = self.gs_path

        if update_from_store:
            df = Datafile(path)
        else:
            df = Datafile(
                path,
                ignore_stored_metadata=False,
                tags=self.get_tags_from_instance(),
                labels=self.get_labels_from_instance(),
            )

        if df.id != str(self.id):
            logger.warning(
                "Datafile at %s has bound id %s but that does not match this instance id %s. Re-sync your database to the store.",
                self.gs_path,
                df.id,
                str(self.id),
            )

        return df

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
        :param update_db_metadata: If database entry for this file is found, ensure the metadata in that row is up to date with metadata from the cloud store. If false, the instance returned may be dirty (i.e. be set with values from teh store that do not correspond to the database)
        :type update_db_metadata: bool
        :return: Instance of db model
        :rtype: AbstractSynchronisedDatastore
        """

        created = False
        try:
            instance = cls.objects.get(id=datafile.id)
            instance.update_instance_from_tags(datafile.tags)
            instance.update_instance_from_labels(datafile.labels)
            if update_db_metadata:
                instance.save()

        except cls.DoesNotExist:
            instance = cls(id=datafile.id)
            instance.update_instance_from_tags(datafile.tags)
            instance.update_instance_from_labels(datafile.labels)

            # Set the file field .name attribute directly to path (https://stackoverflow.com/a/10906037/3556110)
            getattr(instance, cls.__FILE_FIELD__).name = datafile.path_in_bucket

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
        """Return the storage object for this Datastore"""
        mapped_fields = dict((field.attname, field) for field in cls._meta.concrete_fields)
        return mapped_fields[cls.__FILE_FIELD__].storage

    @classmethod
    def get_storage_settings(cls):
        """Return a dict of settings of the storage for this Datastore"""
        mapped_fields = dict((field.attname, field) for field in cls._meta.concrete_fields)
        return mapped_fields[cls.__FILE_FIELD__].store["storage_settings"]

    @property
    def _location(self):
        """The location within the bucket of the file, including name and extension, eg 'folder/subfolder/file_name.txt'
        Note that this path may not yet actually exist within the bucket, if the instance is not yet added this is what
        *will* be saved (or, at least, what will be attempted)
        """
        if getattr(self._file_field, "name", "") != "":
            return self._file_field.name
        else:
            return None

    @property
    def gs_path(self):
        """The qualified pathway of this object on GCS, or None if the blob has no name attribute"""
        loc = self._location
        if loc is not None:
            return f"gs://{self._storage.bucket_name}/{loc}"

    def _serialise_metadata(self, metadata):
        """Encode metadata as a dictionary of JSON strings."""
        if not isinstance(metadata, dict):
            raise TypeError(f"Metadata for Google Cloud storage should be a dictionary; received {metadata!r}")

        return {key: json.dumps(value, cls=OctueJSONEncoder) for key, value in metadata.items()}

    def save(self, *args, **kwargs):
        """Override the save method to add metadata to the object saved to the cloud store"""

        # Create a hypothetical (doesn't care if it's remote or local, or never existing)
        #  datafile instance simply to generate octue-compliant metadata
        datafile = self.to_datafile(update_from_store=False, allow_no_location=True)

        # Attach metadata to the file object before saving it
        self.file.file.metadata = self._serialise_metadata(datafile.metadata())
        super().save(*args, **kwargs)
