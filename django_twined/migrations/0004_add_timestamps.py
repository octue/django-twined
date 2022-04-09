# Disable for migrations:
# pylint: disable=missing-docstring

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_twined", "0003_rename_slug_to_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="answered",
            field=models.DateTimeField(blank=True, help_text="When the question was answered", null=True),
        ),
        migrations.AddField(
            model_name="question",
            name="asked",
            field=models.DateTimeField(blank=True, help_text="When the question was asked", null=True),
        ),
    ]
