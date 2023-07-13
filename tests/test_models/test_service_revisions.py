# Disables for testing:
# pylint: disable=missing-docstring

from django.test import TestCase
from django_twined.models.service_revisions import ServiceRevision, service_revision_is_latest_semantic_version


class TestServiceRevisionIsLatestSemanticVersion(TestCase):
    NAMESPACE = "my-org"
    NAME = "my-service"

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
        """Ensure that a service revision's topic is correct."""
        sr = ServiceRevision.objects.create(
            project_name="gargantuan-gibbons",
            namespace="large-gibbons",
            name="gibbon-analyser",
            tag="1.0.0",
        )

        self.assertEqual(sr.topic, "octue.services.large-gibbons.gibbon-analyser.1-0-0")

    def test_create_with_defaults(self):
        """Ensure that default settings are read for creating default entries in the db"""
        sr = ServiceRevision.objects.create(name="gibbon-analyser")
        self.assertEqual(sr.namespace, "test-default-namespace")
        self.assertEqual(sr.project_name, "test-default-project-name")
        self.assertEqual(sr.tag, "test-default-tag")

    def test_only_one_revision_of_a_service_can_be_default(self):
        """Test that, when a new default revision is created for a service, the previous default revision has its
        default status removed.
        """
        namespace = "large-gibbons"
        name = "gibbon-analyser"

        ServiceRevision.objects.create(namespace=namespace, name=name, tag="0.1.0", is_default=True)
        self.assertTrue(ServiceRevision.objects.get(namespace=namespace, name=name, tag="0.1.0").is_default)

        ServiceRevision.objects.create(namespace=namespace, name=name, tag="0.2.0", is_default=True)
        self.assertTrue(ServiceRevision.objects.get(namespace=namespace, name=name, tag="0.2.0").is_default)
        self.assertFalse(ServiceRevision.objects.get(namespace=namespace, name=name, tag="0.1.0").is_default)
