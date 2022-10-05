# Disable for migrations:
# pylint: disable=missing-docstring

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("django_twined", "0002_slug_unique_and_not_editable"),
    ]

    operations = [
        migrations.RenameField(
            model_name="abstractregisteredservice",
            old_name="slug",
            new_name="name",
        ),
    ]
