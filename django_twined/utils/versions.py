import packaging.version
from django_twined.models import ServiceRevision


def service_revision_is_latest_semantic_version(service_revision):
    """Determine if a service revision is the latest semantic version based on its revision tag.

    :param django_twined.models.service_revision.ServiceRevision namespace: the service revision to heck
    :return bool: `True` if the service revision is the latest semantic version according to its revision tag
    """
    sorted_service_revisions = sorted(
        [
            *ServiceRevision.objects.filter(namespace=service_revision.namespace, name=service_revision.name),
            service_revision,
        ],
        key=lambda revision: packaging.version.parse(revision.tag),
    )

    return sorted_service_revisions[-1] == service_revision
