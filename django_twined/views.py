import json

from django.http import JsonResponse
from django_twined.models import ServiceRevision


def service_revision(request, namespace, name):
    """Get or create a service revision. If, when getting a service revision, the revision tag isn't provided, the
    latest revision for that service is returned.

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
                service_revision = ServiceRevision.objects.get(namespace=namespace, name=name, tag=revision_tag)

            else:
                service_revision = (
                    ServiceRevision.objects.filter(
                        namespace=namespace,
                        name=name,
                    )
                    .order_by("tag")
                    .last()
                )

        except ServiceRevision.DoesNotExist:
            return JsonResponse({"success": False, "error": "Service revision not found."}, status=404)

        return JsonResponse(
            {
                "success": True,
                "namespace": namespace,
                "name": name,
                "revision_tag": service_revision.tag,
                "is_default": service_revision.is_default,
            },
            status=200,
        )

    if request.method == "POST":
        body = json.loads(request.body)

        if "revision_tag" not in body:
            return JsonResponse(
                {"success": False, "error": "A revision tag must be included when registering a new service revision"},
                status=400,
            )

        ServiceRevision.objects.create(
            namespace=namespace,
            name=name,
            tag=body["revision_tag"],
            is_default=body.get("is_default", False),
        )

        return JsonResponse({"success": True}, status=201)

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)
