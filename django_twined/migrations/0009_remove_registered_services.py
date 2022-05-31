# Disable for migrations:
# pylint: disable=missing-docstring

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("django_twined", "0008_registered_relations_to_nullable"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="registeredservice",
            name="abstractregisteredservice_ptr",
        ),
        migrations.RemoveField(
            model_name="question",
            name="registered_service",
        ),
        migrations.DeleteModel(
            name="AbstractRegisteredService",
        ),
        migrations.DeleteModel(
            name="RegisteredService",
        ),
    ]
