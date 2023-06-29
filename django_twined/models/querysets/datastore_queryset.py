import logging

from django.db import transaction
from django.db.models.query import QuerySet
from django.db.utils import IntegrityError
from octue.resources import Datafile, Dataset


logger = logging.getLogger(__name__)


class StoreComparison:
    """Tiny class simply present to hold sets of IDs for store comparisons"""

    def __init__(
        self,
        datafiles_in_store,
        ids_in_store,
        ids_already_present,
        ids_missing_from_store,
        ids_missing_from_db,
        ids_imported=None,
        ids_failed_to_import=None,
        ids_synced=None,
        ids_failed_to_sync=None,
    ):
        self.datafiles_in_store = datafiles_in_store
        self.ids_in_store = ids_in_store
        self.ids_already_present = ids_already_present
        self.ids_missing_from_store = ids_missing_from_store
        self.ids_missing_from_db = ids_missing_from_db
        self.ids_imported = ids_imported
        self.ids_failed_to_import = ids_failed_to_import
        self.ids_synced = ids_synced
        self.ids_failed_to_sync = ids_failed_to_sync

    def __str__(self):

        out = ""
        for symbol in [
            "datafiles_in_store",
            "ids_in_store",
            "ids_already_present",
            "ids_missing_from_store",
            "ids_missing_from_db",
            "ids_imported",
            "ids_failed_to_import",
            "ids_synced",
            "ids_failed_to_sync",
        ]:
            out += f"{symbol}: {getattr(self,symbol)}\n"
        return out


class DatastoreQuerySetMixin:
    """A queryset mixin enabling use of django querysets as Datasets for Octue.
    Either use DatastoreQueryset directly, or use this to mix in additional queryset methods.
    """

    def delete_files(self, include_rows=True):
        """Delete the files corresponding to the rows in this query from the datalake"""
        # Get a list of filenames to delete
        files_to_delete = self.values_list(self.model.__FILE_FIELD__, flat=True)

        # Delete the datafiles from GCS
        bucket = self.model.get_storage().bucket
        for file in files_to_delete:
            bucket.blob(file).delete()

        # Run deletion of the queryset in a transaction so the database row gets restored if the file cannot be deleted
        if include_rows:
            return self.delete()

    def __init__(self, *args, store_comparison=None, **kwargs):
        self.store_comparison = store_comparison
        super().__init__(*args, **kwargs)

    def get_dataset(self, name, queryset, **kwargs):
        """Turn a django queryset into a dataset
        The queryset must be from a model that inherits from AbstractSynchronisedDatastore

        Note that this method does evaluate the full queryset with Queryset.all(), rather than yielding entries.

        :param name: The name of the dataset
        :type name: string
        :param kwargs: Optional additional keyword arguments to the octue.Dataset() constructor, e.g. {'id': '<uuid>'}
        :type kwargs: dict
        :return: The created dataset
        :rtype: octue.resources.Dataset
        """
        return Dataset(name=name, files=[*queryset.all()], **kwargs)

    def compare_store(self, cloud_paths=None):
        """Compares the contents of the store for files whose presence is not recorded in the database and imports them.

        Ignores the queryset; this method operates identically irrespective of whether called on a filtered queryset or not.

        :param list|None cloud_paths: A list of cloud_paths to import (eg ['gs://folder/file1.txt', 'gs://folder/file2.txt'].
        Import will be limited only to these paths (if they exist and those files are not already present in the store)).

        :return tuple(s): sets of ids for the resulting (imported, already_present, failed_to_import, missing_from_store) records,
        enabling further operations (such as syncing already present records from store)
        """

        if cloud_paths is not None:
            raise ValueError("cloud_paths not implemented yet")

        # Get the store to use
        storage = self.model.get_storage()

        # Get a set of ids of all existing objects, and a dict of Datafile objects keyed on their id
        ids_in_db = set(self.model.objects.values_list("id", flat=True))

        # Get a dict of Datafile objects keyed on their id, one for each object in the store
        datafiles_in_store = dict()
        for blob in storage.client.list_blobs(bucket_or_name=storage.bucket_name):
            # Get the gs path of the object
            gs_path = f"gs://{storage.bucket_name}/{blob.name}"
            logger.debug(f"Synchronizing metadata -> database for store object {gs_path}")

            # TODO This is not scalable. It will become untenable for hundreds of objects,
            # because it fetches metadata individually so generates N requests to the store.
            # Figure out whether we can list_blobs with their metadata in one request.
            datafile = Datafile(gs_path)

            # Note - datafile.id is a UUID, not the
            # same as blob.id which is a weird form of google path string
            datafiles_in_store[datafile.id] = datafile

        # Get a set of ids of all objects existing in the store
        ids_in_store = set(datafiles_in_store.keys())

        # Ids of datafiles which are both in the store and the database
        ids_already_present = ids_in_store.intersection(ids_in_db)

        # Ids of datafiles which are in the database but not the store (require deletion)
        ids_missing_from_store = ids_in_db.difference(ids_already_present)

        # Ids of datafiles which are in the store but not the database (require creation)
        ids_missing_from_db = ids_in_store.difference(ids_already_present)

        self.store_comparison = StoreComparison(
            datafiles_in_store, ids_in_store, ids_already_present, ids_missing_from_store, ids_missing_from_db
        )

        return self

    def import_missing(self):
        """Where files exist in the datastore but not the database, import those records to the DB"""

        if self.store_comparison is None:
            self = self.compare_store()

        # Prepare new records for creation in the db
        # TODO This is not scalable, we have N database inserts for N files.
        #  We could do this quicker in a bulk_create. However, failures to
        #  insert would create an all-or-nothing problem. Perhaps we can fall
        #  back to linear create on batches that fail to bulk_create?
        failed = list()
        imported = list()
        datafiles_in_store = self.store_comparison.datafiles_in_store
        for datafile_id in self.store_comparison.ids_missing_from_db:
            # Each update has to be in a transaction or the outer transaction gets left dirty after the first failure
            with transaction.atomic():
                try:
                    self.model.from_datafile(datafiles_in_store[datafile_id])
                    imported.append(datafile_id)
                except IntegrityError as e:
                    logger.error(
                        f"Could not create record from datastore object {datafiles_in_store[datafile_id].path}. Check the metadata on that file. Error was: {str(e)}"
                    )
                    failed.append(datafile_id)

        self.store_comparison.ids_imported = set(imported)
        self.store_comparison.ids_failed_to_import = set(failed)

        return self

    def delete_missing(self):
        """Where files are absent from the datastore, but there are records in the database, delete those records"""
        if self.store_comparison is None:
            self = self.compare_store()

        self.filter(id__in=self.store_comparison.ids_missing_from_store).delete()

        return self

    def sync_metadata_from_store(self):
        """Take a queryset of files and update their metadata records from the store

        This ensures that file records (metadata) are consistent with the source of truth (the datastore).

        :param bool allow_delete: If true (the default), records of files not present in the store will be
        deleted. This defaults to true in order to follow the pattern that the datastore is the source of truth.
        """

        if self.store_comparison is None:
            self = self.compare_store()

        ids_to_sync = set(str(id) for id in self.values_list("id")[0])

        # Update records with datafile meta
        # TODO This is not scalable, we have N database inserts for N files.
        #  We could do this quicker in a bulk_update. However, failures to
        #  insert would create an all-or-nothing problem. Perhaps we can fall
        #  back to linear create on batches that fail to bulk_update?
        failed = list()
        synced = list()
        datafiles_in_store = self.store_comparison.datafiles_in_store
        for id in ids_to_sync:
            # Each update has to be in a transaction or the outer transaction gets left dirty after the first failure
            with transaction.atomic():
                try:
                    self.model.from_datafile(datafiles_in_store[id], update_db_metadata=True)
                    synced.append(id)

                except IntegrityError as e:
                    logger.error(
                        f"Could not update record from datastore object {datafiles_in_store[id].path}. Check the metadata on that file. Error was: {str(e)}"
                    )
                    failed.append(id)

        self.store_comparison.ids_synced = set(synced)
        self.store_comparison.ids_failed_to_sync = set(failed)

        return self


class DatastoreQueryset(DatastoreQuerySetMixin, QuerySet):
    pass
