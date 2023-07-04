import packaging.version
from django_twined.models import ServiceRevision


def select_latest_service_revision_by_semantic_version(namespace, name):
    """Select the latest service revision by the semantic version used for its tag.

    :param str namespace: the namespace of the service
    :param str name: the name of the service
    :return django_twined.models.service_revisions.ServiceRevision: the service revision whose tag is the latest semantic version
    """
    sorted_service_revisions = sorted(
        ServiceRevision.objects.filter(namespace=namespace, name=name),
        key=lambda revision: packaging.version.parse(revision.tag),
    )

    return sorted_service_revisions[-1]
