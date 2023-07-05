# Disables for testing:
# pylint: disable=missing-docstring

from django.test import TestCase, override_settings
from django_twined.models.service_revisions import ServiceRevision, service_revision_is_latest_semantic_version


class TestServiceRevisionIsLatestSemanticVersion(TestCase):
    NAMESPACE = "my-org"
    NAME = "my-service"

    def test_revision_with_non_semantic_version_tag_not_found_to_be_latest_version(self):
        """Test that a service revisions with a tag that isn't a semantic versions is not found to be the latest
        version.
        """
        ServiceRevision.objects.create(namespace=self.NAMESPACE, name=self.NAME, tag="0.1.0")
        ServiceRevision.objects.create(namespace=self.NAMESPACE, name=self.NAME, tag="2.1.0", is_default=True)

        new_revision = ServiceRevision(namespace=self.NAMESPACE, name=self.NAME, tag="hello")
        self.assertFalse(service_revision_is_latest_semantic_version(new_revision))

    def test_revision_with_larger_semantic_version_found_to_be_latest_version(self):
        """Test that a service revision with a semantic version that is naturally/semantically, but not alphabetically,
        larger than the version of the default revision is not found to be the latest version.
        """
        ServiceRevision.objects.create(namespace=self.NAMESPACE, name=self.NAME, tag="0.1.0")
        ServiceRevision.objects.create(namespace=self.NAMESPACE, name=self.NAME, tag="2.1.0", is_default=True)

        new_revision = ServiceRevision(namespace=self.NAMESPACE, name=self.NAME, tag="11.1.0")
        self.assertTrue(service_revision_is_latest_semantic_version(new_revision))

    def test_larger_non_candidate_version_considered_newer_than_smaller_candidate_versions(self):
        """Test that a service revision with a version tag that doesn't contain a candidate part and is semantically
        larger than exising revisions' version tags is considered a later version than the existing revisions (i.e. that
        `2.2.0` is seen as newer than `2.1.0.beta-2`).
        """
        ServiceRevision.objects.create(namespace=self.NAMESPACE, name=self.NAME, tag="2.1.0.beta-1")
        ServiceRevision.objects.create(namespace=self.NAMESPACE, name=self.NAME, tag="2.1.0.beta-2", is_default=True)

        new_revision = ServiceRevision(namespace=self.NAMESPACE, name=self.NAME, tag="2.2.0")
        self.assertTrue(service_revision_is_latest_semantic_version(new_revision))

    def test_non_candidate_version_considered_newer_than_candidate_versions_for_same_version(self):
        """Test that a service revision with no candidate part in its version tag is considered to be a later version
        than a service revision with the same semantic version except for including a candidate part (i.e. that `2.1.0`
        is seen as newer than `2.1.0.beta-1`).
        """
        ServiceRevision.objects.create(namespace=self.NAMESPACE, name=self.NAME, tag="2.1.0.beta-1")
        ServiceRevision.objects.create(namespace=self.NAMESPACE, name=self.NAME, tag="2.1.0.beta-2", is_default=True)

        new_revision = ServiceRevision(namespace=self.NAMESPACE, name=self.NAME, tag="2.1.0")
        self.assertTrue(service_revision_is_latest_semantic_version(new_revision))

    def test_alphabetically_largest_candidate_version_considered_latest(self):
        """Test that a service revision with the same semantic version apart from the candidate part is considered the
        latest if it has the alphabetically largest candidate part.
        """
        ServiceRevision.objects.create(namespace=self.NAMESPACE, name=self.NAME, tag="2.1.0.beta-1")
        ServiceRevision.objects.create(namespace=self.NAMESPACE, name=self.NAME, tag="2.1.0.beta-2", is_default=True)

        new_revision = ServiceRevision(namespace=self.NAMESPACE, name=self.NAME, tag="2.1.0.beta-3")
        self.assertTrue(service_revision_is_latest_semantic_version(new_revision))


class ServiceRevisionTestCase(TestCase):
    def test_topic(self):
        """Ensure that default settings are read for creating default entries in the db"""
        sr = ServiceRevision.objects.create(
            project_name="gargantuan-gibbons", namespace="large-gibbons", name="gibbon-analyser", tag="latest"
        )

        self.assertEqual(sr.topic, "octue.services.large-gibbons.gibbon-analyser.latest")

    def test_topic_with_blank_namespace_and_tag(self):
        """Ensure that default settings are read for creating default entries in the db"""
        with override_settings(TWINED_DEFAULT_NAMESPACE=""):
            with override_settings(TWINED_DEFAULT_TAG=""):
                sr = ServiceRevision.objects.create(project_name="gargantuan-gibbons", name="gibbon-analyser")
            self.assertEqual(sr.topic, "octue.services.gibbon-analyser")

    def test_create_with_defaults(self):
        """Ensure that default settings are read for creating default entries in the db"""

        sr = ServiceRevision.objects.create(
            name="gibbon-analyser",
        )

        self.assertEqual(sr.namespace, "test-default-namespace")
        self.assertEqual(sr.project_name, "test-default-project-name")
        self.assertEqual(sr.tag, "test-default-tag")