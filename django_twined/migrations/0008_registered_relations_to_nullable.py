# Disable for migrations:
# pylint: disable=missing-docstring

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_twined", "0007_registered_to_revision"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="registered_service",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="questions",
                to="django_twined.registeredservice",
            ),
        )
    ]
