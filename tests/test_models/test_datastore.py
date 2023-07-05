# Disables for testing:
# pylint: disable=missing-docstring

from unittest import skipIf

from django.test import TestCase as BaseTestCase


class DatastoreTestCase(BaseTestCase):
    @skipIf(True, "Generic Datastore tests not abstracted from data lakes MyDatalakeModel tests yet")
    def test_alter_metadata_fails_if_propagation_prevented(self):
        pass

    @skipIf(True, "Generic Datastore tests not abstracted from data lakes MyDatalakeModel tests yet")
    def test_alter_metadata_succeeds_if_propagation_allowed(self):
        pass

    @skipIf(True, "Generic Datastore tests not abstracted from data lakes MyDatalakeModel tests yet")
    def test_alter_file_fails_always(self):
        pass

    @skipIf(True, "Generic Datastore tests not abstracted from data lakes MyDatalakeModel tests yet")
    def test_create_file_adds_metadata(self):
        pass

    @skipIf(True, "Generic Datastore tests not abstracted from data lakes MyDatalakeModel tests yet")
    def test_get_datafile(self):
        pass

    @skipIf(True, "Generic Datastore tests not abstracted from data lakes MyDatalakeModel tests yet")
    def test_sync_datastore(self):
        pass


# import tempfile

# import uuid
# from django.conf import settings
# from django.core.files.base import ContentFile
# from django.test import TestCase
# from octue.resources import Datafile

# from datalake.models import MyDatalakeModel
# from ..base import CallCommandMixin


# class DatalakeTestCase(CallCommandMixin, TestCase):
#     """
#     # ABOUT DATALAKES

#     ## Source of truth

#     We consider the files and the metadata on them to be the source of truth. Why?

#     - To ensure modularity of the collection of technologies and services.
#         If services such able to read from and write to the data lakes
#         without interacting with the main django app, we can build a collection of loosely-coupled
#         services whose scope is very tight: "do some operation with one or more data files"
#         This service needs to know NOTHING about how the django app operates so can be built and
#         maintained independently.

#     - To simplify service deployment and aid security.
#         If services accessing the datafiles require access either to the django server or the
#         guts of the database that backs it, they'll have to a) be production hardened to the same
#         standard, b) be developed only by teams we trust to the same level as the core app team
#         and c) have the appropriate credentials injected into them, leaving a significantly
#         larger attack surface.

#     - Because the data is in the same place.
#         Fundamentally, you should keep metadata about files in the same place as the files.

#     - To speed up systems.
#         Making one call to the GCS api to stream the file metadata and its contents is much
#         quicker and easier than making one call to get the file, then another call somewhere
#         else to get the correct metadata.

#     ## What are the requirements?

#     - From django admin, we need to create a datalake file entry, with new data.
#         That new data should be saved with metadata on GCP, where the metadata corresponds to the saved database row.

#     - From django admin, we need to edit a datalake file entry, to update the metadata only.
#         The new metadata should propagate to GCP on the same file object.

#     - From django admin, we need to be able to trigger an 'update metadata' task on a list of files.
#         This task will take existing metadata from existing files and update the database row.

#     - From django admin, we need to EITHER::DECISION REQUIRED:
#         a) Be able to edit file contents, which updates the actual object contents on GCS whilst retaining the same
#            unique object.
#                 - PROS: Quickly find a file and change it
#                 - CONS: Not easily auditable

#         b) NOT be able to update an object. This ensures objects are always unique and are thus auditable by UUID only.
#            The use case of editing a file would be addressed by simply adding a new file (the edited version) and replacing
#            the old one in any relations
#                 - PROS: Easily auditable use of which objects were used in a question.
#                 - CONS: If object contents are changed, that's presently not tracked other than by object hash so
#                         potentially still difficult to reconstruct.
#                 - CONS: In the workflow for updating a datafile each month, this requires additional effort to
#                         add or replace files where you have to copy the metadata each time. Need to add a
#                         feature to the django admin to help ease this pain

#     - Need to override django storage client to prevent creation of additional files on attempt to edit file in the db. It
#         should create new **versions** of that file, not new **files**

#     - [OPTIONAL] Need to alert django when a file is added or updated on GCS.
#         Why? So that django's file records are constantly in sync, as opposed to only in sync as and when we run the periodic
#         synchronisation.
#         Because we do not run django on Cloud Run, we cannot trigger it directly from PubSub events (a PS event is created in GCP
#         for any and every GCS edit). However, by creation of an ultra-lightweight service e.g. on Google Cloud Functions (which
#         *is* triggerable off of pubsub), we can notify django that updates have happened via a webhook.

#     - If a file is deleted from GCS, its corresponding record, if it exists, should be deleted from django on sync.

#     - If windquest attempts to delete a file, it should not be allowed to.

#     - If file metadata is updated in GCS, a synchronisation task (run either on that record or the whole store) should propagate it
#         to django because it is the source of truth, not django

#     """

#     def test_get_datafile_from_empty_or_unsaved_instance(self):

#         mts = MyDatalakeModel()
#         self.assertIsNone(
#             mts.datafile, "MyDatalakeModel.datafile should return none if no file has been associated with it",
#         )

#         mts2 = MyDatalakeModel(file=ContentFile("hello world", name="something.txt"))
#         self.assertIsNone(
#             mts2.datafile,
#             "MyDatalakeModel.datafile should return none if a local file exists, but it it not in the store",
#         )

#     def test_creating_new_file_in_admin_propagates_new_metadata(self):
#         """
#         From django admin, we need to create a datalake file entry, with new data.
#         That new data should be saved with metadata on GCP, where the metadata corresponds to the saved database row.
#         """

#         # Create datafile (never mind the contents) and save as a MyDatalakeModel entry
#         file = ContentFile("hello world".encode("utf-8"), name="something.txt")
#         mts = MyDatalakeModel(
#             file=file, my_parameter_1=2, my_parameter_2=221, my_parameter_3=12, my_parameter_4=13, my_parameter_5="something",
#         )
#         mts.save()

#         # Independently fetch the datafile from GCS, outside of django's storage mechanism
#         datafile = Datafile(mts.gs_path, project_name=mts.project_name)

#         # Assert that the metadata has been correctly attached
#         self.assertEqual(str(mts.id), datafile.id)
#         self.assertEqual(datafile.tags.get("my_parameter_1"), 2)

#     def test_update_row_updates_store_metadata(self):
#         """
#         - From django admin, we need to edit a datalake file entry, to update the metadata only.
#             The new metadata should propagate to GCP on the same file object.
#         """

#         file = ContentFile("hello world".encode("utf-8"), name="something.txt")
#         mts = MyDatalakeModel(
#             file=file, my_parameter_1=2, my_parameter_2=221, my_parameter_3=12, my_parameter_4=13, my_parameter_5="something",
#         )
#         mts.save()

#         mts.my_parameter_1 = 0
#         mts.save()

#         datafile = Datafile(mts.gs_path, project_name=mts.project_name)

#         self.assertEqual(datafile.tags.get("my_parameter_1"), 0)

#     def test_updating_file_does_not_create_new_gcs_object(self):
#         """
#         - Need to override django storage client to prevent creation of additional files on attempt to edit file in the db. It
#           should create new **versions** of that file, not new **files**
#         - Need to be able to edit file contents, which updates the actual object contents on GCS whilst retaining the same
#           unique object record.
#         """
#         original_tags = {
#             "my_parameter_1": 2,
#             "my_parameter_2": 122,
#             "my_parameter_3": 12,
#             "my_parameter_4": 22,
#             "my_parameter_5": "a-string"
#         }
#         name = f"{str(uuid.uuid4())[0:7]}.txt"
#         file = ContentFile("hello world".encode("utf-8"), name=name)
#         mts = MyDatalakeModel(file=file, **original_tags)
#         mts.save()

#         original_file_name = mts.file.file
#         mts.file = ContentFile("Bye world".encode("utf-8"), name=name)
#         mts.save()

#         # Assert file name is the same
#         self.assertEqual(str(mts.file.file), str(original_file_name))

#         # Assert the tags haven't changed
#         datafile = Datafile(mts.gs_path, project_name=mts.project_name)
#         self.assertEqual(datafile.tags, original_tags)

#         # Assert that the file contents for the original mts record is updated
#         with datafile as (df, f):
#             contents = f.read()
#             self.assertTrue("Bye world" in contents)

#     def test_import_missing_will_create_new_records(self):
#         """
#         - From django admin, we need to be able to trigger an 'update metadata' task on a list of files.
#             This task will take existing metadata from existing files and update the database row.
#         """

#         # Create a datafile and upload it into storage
#         store = settings.TWINED_DATA_STORES["my-store"]["storage_settings"]
#         tags = {
#             "my_parameter_1": 2,
#             "my_parameter_2": 122,
#             "my_parameter_3": 12,
#             "my_parameter_4": 22,
#             "my_parameter_5": "sync-meta-test",
#         }
#         labels = {"my-store-label"}

#         # Create a list of datafiles we want to sync to the db
#         gs_paths_to_sync = list()

#         # Create a normal local .txt file
#         id = str(uuid.uuid4())
#         with tempfile.NamedTemporaryFile(suffix=".txt", mode="w") as fp:
#             fp.write('{"my":"data"}')

#             # Upload the local file to gcloud, with octue metadata
#             with Datafile(path=fp.name, tags=tags, labels=labels, mode="r", id=id) as (datafile, f):
#                 gs_path = f"gs://{store['bucket_name']}{datafile.path}"
#                 datafile.to_cloud(project_name=store["project_id"], cloud_path=gs_path)

#                 # Add to the sync list
#                 gs_paths_to_sync.append(gs_path)

#         # Assert that it's not created yet
#         with self.assertRaises(MyDatalakeModel.DoesNotExist):
#             MyDatalakeModel.objects.get(id=id)

#         # Run the import
#         # TODO implement cloud_paths so that tests are idempotent
#         # MyDatalakeModel.objects.compare_store(cloud_paths=gs_paths_to_sync).import_missing()
#         MyDatalakeModel.objects.import_missing()

#         # Get the imported record
#         imported = MyDatalakeModel.objects.get(id=id)
#         self.assertEqual(imported.my_parameter_1, tags["my_parameter_1"])
#         self.assertEqual(imported.my_parameter_5, tags["my_parameter_5"])

#     def test_deleted_objects_are_removed_from_db_on_sync(self):
#         """
#         If a file is deleted from GCS, its corresponding record, if it exists, should be deleted from django on the next sync.
#         """

#         # Create datafile (never mind the contents) and save as a MyDatalakeModel entry
#         file = ContentFile("hello world".encode("utf-8"), name="something.txt")
#         mts = MyDatalakeModel(
#             file=file, my_parameter_1=2, my_parameter_2=221, my_parameter_3=12, my_parameter_4=13, my_parameter_5="something",
#         )
#         mts.save()

#         # Independently delete the datafile from GCS, outside of django's storage mechanism
#         storage = MyDatalakeModel.get_storage()
#         blob = storage.bucket.blob(mts.file.name)
#         blob.delete()

#         # The row should still exist right now, even though the file is gone
#         self.assertEqual(MyDatalakeModel.objects.filter(id=mts.id).count(), 1)

#         # Use the manager to delete missing entries, and assert that the row has gone
#         MyDatalakeModel.objects.delete_missing()
#         self.assertEqual(MyDatalakeModel.objects.filter(id=mts.id).count(), 0)

#     def test_changed_file_metadata_in_store_gets_updated_to_db_on_sync(self):
#         """If file metadata is updated in GCS, a synchronisation task (run either on that
#         record or the whole store) should propagate it to django (because the store is the
#         source of truth, not django)
#         """

#         # Create datafile (never mind the contents) and save as a MyDatalakeModel entry
#         file = ContentFile("hello world".encode("utf-8"), name="something.txt")
#         mts = MyDatalakeModel(
#             file=file, my_parameter_1=2, my_parameter_2=221, my_parameter_3=12, my_parameter_4=13, my_parameter_5="something",
#         )
#         mts.save()

#         # Independently update the file's metadata, outside of django's storage mechanism
#         datafile = Datafile(mts.gs_path, project_name=mts.project_name)
#         datafile.tags["my_parameter_1"] = 3
#         datafile.update_cloud_metadata()

#         # No sync has happened; querying the metadata should result in the original value
#         self.assertEqual(str(mts.id), datafile.id)
#         mts.refresh_from_db()
#         self.assertEqual(mts.my_parameter_1, 2)

#         # Perform the sync; only on this file
#         MyDatalakeModel.objects.filter(id=mts.id).sync_metadata_from_store()

#         mts.refresh_from_db()
#         self.assertEqual(mts.my_parameter_1, 3)

#     def test_invalidated_meta_fails_to_update_db_on_sync(self):
#         """If file metadata becomes invalid in GCS prior to a synchronisation, an
#         integrityError should be raised
#         """

#         # Create datafile (never mind the contents) and save as a MyDatalakeModel entry
#         file = ContentFile("hello world".encode("utf-8"), name="something.txt")
#         mts = MyDatalakeModel(
#             file=file, my_parameter_1=2, my_parameter_2=221, my_parameter_3=12, my_parameter_4=13, my_parameter_5="something",
#         )
#         mts.save()

#         # Independently update the file's metadata to be invalid
#         datafile = Datafile(mts.gs_path, project_name=mts.project_name)
#         datafile.tags = {}
#         datafile.update_cloud_metadata()

#         # Perform the sync
#         qs = MyDatalakeModel.objects.filter(id=mts.id).sync_metadata_from_store()
#         self.assertIn(str(mts.id), qs.store_comparison.ids_failed_to_sync)

#         mts.refresh_from_db()
#         self.assertEqual(mts.my_parameter_1, 2)

#     def test_row_deletion_does_not_remove_datalake_file(self):
#         """If we delete a file row, it should not get removed from the datalake."""

#         # Create datafile (never mind the contents) and save as a MyDatalakeModel entry
#         mts = MyDatalakeModel(
#             file=ContentFile("hello world".encode("utf-8"), name="something.txt"),
#             my_parameter_1=2,
#             my_parameter_2=221,
#             my_parameter_3=12,
#             my_parameter_4=13,
#             my_parameter_5="something",
#         )
#         mts.save()

#         # Delete the actual object from the DB
#         mts.delete()

#         # Independently update the file's metadata, outside of django's storage mechanism
#         datafile = Datafile(mts.gs_path, project_name=mts.project_name)
#         self.assertTrue(datafile.exists_in_cloud)
#         self.assertEqual(MyDatalakeModel.objects.filter(id=mts.id).count(), 0)

#     def test_queryset_object_delete_removes_datalake_files(self):
#         """If we deletes a file row, it should not get removed from the datalake."""

#         # Create two datafiles
#         mts1 = MyDatalakeModel(
#             file=ContentFile("hello world".encode("utf-8"), name="something.txt"),
#             my_parameter_1=2,
#             my_parameter_2=221,
#             my_parameter_3=12,
#             my_parameter_4=13,
#             my_parameter_5="something",
#         )
#         mts1.save()
#         mts2 = MyDatalakeModel(
#             file=ContentFile("hello world".encode("utf-8"), name="somethingelse.txt"),
#             my_parameter_1=3,
#             my_parameter_2=0,
#             my_parameter_3=1,
#             my_parameter_4=2,
#             my_parameter_5="somethingelse",
#         )
#         mts2.save()

#         # Use the manager to do an object delete
#         MyDatalakeModel.objects.filter(id=mts1.id).delete_files(include_rows=True)

#         # Check it's been deleted from the bucket and the DB
#         names = set(blob.name for blob in MyDatalakeModel.get_storage().bucket.list_blobs())
#         self.assertFalse(mts1.file.name in names)
#         self.assertEqual(MyDatalakeModel.objects.filter(id=mts1.id).count(), 0)
#         self.assertEqual(MyDatalakeModel.objects.filter(id=mts2.id).count(), 1)

#     # def test_update_metadata_task_syncs_metadata_from_store_into_db(self):
#     #     """
#     #     - From django admin, we need to be able to trigger an 'update metadata' task on a list of files.
#     #         This task will take existing metadata from existing files and update the database row.
#     #     """
#     #     self.fail()
