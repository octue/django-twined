# Disable for migrations:
# pylint: disable=missing-docstring

from django.db import migrations


def forward(apps, schema_editor):
    """Creates ServiceRevisions from RegisteredServices and updates relations"""

    RegisteredService = apps.get_model("django_twined", "RegisteredService")
    ServiceRevision = apps.get_model("django_twined", "ServiceRevision")
    Question = apps.get_model("django_twined", "Question")

    # Create service revisions from the registered services
    #  (use a simple iterator, as there's only ever a few).
    for registered_service in RegisteredService.objects.all():
        # Use the default namespace, tag and project_name
        service_revision = ServiceRevision.objects.create(topic_id=registered_service.id, name=registered_service.name)

        # Bulk update questions for this service
        Question.objects.filter(registered_service=registered_service).update(service_revision=service_revision)


def reverse(apps, schema_editor):
    """No-op because it's impossible to retrive unique RegisteredServices
    from sets of ServiceRevisions; you need to revert to this point (0007) then
    manually reconstruct the RegisteredServices before continuing.

    At this stage we don't anticipate anyone ever having to do this.

    """


class Migration(migrations.Migration):

    dependencies = [
        ("django_twined", "0006_service_revisions_and_events"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
