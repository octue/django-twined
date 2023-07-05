from django.test import TestCase
from django_twined.models import ServiceRevision
from django_twined.utils.versions import service_revision_is_latest_semantic_version


NAMESPACE = "my-org"
NAME = "my-service"


class TestServiceRevisionIsLatestSemanticVersion(TestCase):
    def test_revision_with_non_semantic_version_tag_not_found_to_be_latest_version(self):
        """Test that a service revisions with a tag that isn't a semantic versions is not found to be the latest
        version.
        """
        ServiceRevision.objects.create(namespace=NAMESPACE, name=NAME, tag="0.1.0")
        ServiceRevision.objects.create(namespace=NAMESPACE, name=NAME, tag="2.1.0", is_default=True)

        new_revision = ServiceRevision(namespace=NAMESPACE, name=NAME, tag="hello")
        self.assertFalse(service_revision_is_latest_semantic_version(new_revision))

    def test_revision_with_larger_semantic_version_found_to_be_latest_version(self):
        """Test that a service revision with a semantic version that is naturally/semantically, but not alphabetically,
        larger than the version of the default revision is not found to be the latest version.
        """
        ServiceRevision.objects.create(namespace=NAMESPACE, name=NAME, tag="0.1.0")
        ServiceRevision.objects.create(namespace=NAMESPACE, name=NAME, tag="2.1.0", is_default=True)

        new_revision = ServiceRevision(namespace=NAMESPACE, name=NAME, tag="11.1.0")
        self.assertTrue(service_revision_is_latest_semantic_version(new_revision))

    def test_larger_non_candidate_version_considered_newer_than_smaller_candidate_versions(self):
        """Test that a service revision with a version tag that doesn't contain a candidate part and is semantically
        larger than exising revisions' version tags is considered a later version than the existing revisions (i.e. that
        `2.2.0` is seen as newer than `2.1.0.beta-2`).
        """
        ServiceRevision.objects.create(namespace=NAMESPACE, name=NAME, tag="2.1.0.beta-1")
        ServiceRevision.objects.create(namespace=NAMESPACE, name=NAME, tag="2.1.0.beta-2", is_default=True)

        new_revision = ServiceRevision(namespace=NAMESPACE, name=NAME, tag="2.2.0")
        self.assertTrue(service_revision_is_latest_semantic_version(new_revision))

    def test_non_candidate_version_considered_newer_than_candidate_versions_for_same_version(self):
        """Test that a service revision with no candidate part in its version tag is considered to be a later version
        than a service revision with the same semantic version except for including a candidate part (i.e. that `2.1.0`
        is seen as newer than `2.1.0.beta-1`).
        """
        ServiceRevision.objects.create(namespace=NAMESPACE, name=NAME, tag="2.1.0.beta-1")
        ServiceRevision.objects.create(namespace=NAMESPACE, name=NAME, tag="2.1.0.beta-2", is_default=True)

        new_revision = ServiceRevision(namespace=NAMESPACE, name=NAME, tag="2.1.0")
        self.assertTrue(service_revision_is_latest_semantic_version(new_revision))

    def test_alphabetically_largest_candidate_version_considered_latest(self):
        """Test that a service revision with the same semantic version apart from the candidate part is considered the
        latest if it has the alphabetically largest candidate part.
        """
        ServiceRevision.objects.create(namespace=NAMESPACE, name=NAME, tag="2.1.0.beta-1")
        ServiceRevision.objects.create(namespace=NAMESPACE, name=NAME, tag="2.1.0.beta-2", is_default=True)

        new_revision = ServiceRevision(namespace=NAMESPACE, name=NAME, tag="2.1.0.beta-3")
        self.assertTrue(service_revision_is_latest_semantic_version(new_revision))
