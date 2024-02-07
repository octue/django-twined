import json

from django.conf import settings
from django.http import JsonResponse
from django_twined.models.service_revisions import ServiceRevision, service_revision_is_latest_semantic_version


SERVICE_REVISION_IS_DEFAULT_CALLBACK = getattr(
    settings,
    "TWINED_SERVICE_REVISION_IS_DEFAULT_CALLBACK",
    service_revision_is_latest_semantic_version,
)


def service_revision(request, namespace, name):
    """Get or create a service revision. If the revision tag isn't provided when getting a service revision, the default
    service revision is returned. This is the service revision with the latest semantic version revision tag by default.

    :param django.core.handlers.wsgi.WSGIRequest request:
    :param str namespace: the namespace of the service
    :param str name: the name of the service
    :return django.http.response.JsonResponse:
    """
    if request.method == "GET":
        # TODO: We can add support for version ranges here later.
        revision_tag = request.GET.get("revision_tag")

        try:
            if revision_tag:
                revision = ServiceRevision.objects.get(namespace=namespace, name=name, tag=revision_tag)
            else:
                revision = ServiceRevision.objects.get(namespace=namespace, name=name, is_default=True)

        except ServiceRevision.DoesNotExist:
            return JsonResponse({"error": "Service revision not found."}, status=404)

        return JsonResponse(
            {
                "namespace": namespace,
                "name": name,
                "revision_tag": revision.tag,
                "is_default": revision.is_default,
            },
            status=200,
        )

    if request.method == "POST":
        body = json.loads(request.body)

        if "revision_tag" not in body:
            return JsonResponse(
                {"error": "A revision tag must be included when registering a new service revision."},
                status=400,
            )

        revision = ServiceRevision(namespace=namespace, name=name, tag=body["revision_tag"])

        if "is_default" in body:
            revision.is_default = body["is_default"]
        elif SERVICE_REVISION_IS_DEFAULT_CALLBACK is not None:
            revision.is_default = SERVICE_REVISION_IS_DEFAULT_CALLBACK(revision)

        revision.save()
        return JsonResponse({}, status=201)

    return JsonResponse({"error": "Invalid request method."}, status=405)
