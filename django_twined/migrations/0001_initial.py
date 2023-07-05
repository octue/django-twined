# Disable for migrations:
# pylint: disable=missing-docstring

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AbstractRegisteredService",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="Service name slug used in django settings to define service credentials"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RegisteredService",
            fields=[
                (
                    "abstractregisteredservice_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="django_twined.abstractregisteredservice",
                    ),
                ),
            ],
            bases=("django_twined.abstractregisteredservice",),
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "registered_service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="questions",
                        to="django_twined.registeredservice",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
