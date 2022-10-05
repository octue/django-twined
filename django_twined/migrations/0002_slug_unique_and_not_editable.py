# Disable for migrations:
# pylint: disable=missing-docstring

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_twined", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="abstractregisteredservice",
            name="slug",
            field=models.SlugField(
                editable=False,
                help_text="Service name (e.g. in cloud run), also used in django settings to define service credentials",
                unique=True,
            ),
        ),
    ]
