# Disable for migrations:
# pylint: disable=missing-docstring

import django_twined.models.service_revisions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_twined", "0009_remove_registered_services"),
    ]

    operations = [
        migrations.AlterField(
            model_name="servicerevision",
            name="project_name",
            field=models.CharField(
                default=django_twined.models.service_revisions.get_default_project_name,
                help_text="The name of the GCP project in which the service resides",
                max_length=80,
            ),
        ),
    ]
