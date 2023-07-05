# Disable for migrations:
# pylint: disable=missing-docstring

import uuid

import django.db.models.deletion
import django_twined.models.service_revisions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_twined", "0005_question_date_help_text"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceRevision",
            fields=[
                ("id", models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When this service revision was created (or, strictly, added to this db)",
                    ),
                ),
                (
                    "namespace",
                    models.SlugField(
                        default=django_twined.models.service_revisions.get_default_namespace,
                        help_text="The organisation namespace, eg 'octue'",
                        max_length=80,
                    ),
                ),
                ("name", models.SlugField(help_text="The name of the service eg 'example-service'")),
                (
                    "tag",
                    models.CharField(
                        default=django_twined.models.service_revisions.get_default_tag,
                        help_text="The service revision tag that helps to identify the unique deployment",
                        max_length=80,
                    ),
                ),
                (
                    "topic_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        help_text="DEPRECATED: The UUID of this service, used for pushing questions to the service via pub/sub",
                    ),
                ),
                (
                    "project_name",
                    models.CharField(
                        default=django_twined.models.service_revisions.get_default_project_name,
                        help_text="The name of the GCP project in which the service resides",
                        max_length=80,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ServiceUsageEvent",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("data", models.JSONField(editable=False, help_text="Event payload")),
                (
                    "kind",
                    models.CharField(
                        blank=False,
                        null=False,
                        choices=[
                            ("q-asked", "Question asked"),
                            ("q-response-updated", "Question response updated"),
                            ("q-status-updated", "Question status updated"),
                        ],
                        help_text="Event kind",
                        max_length=20,
                    ),
                ),
                ("publish_time", models.DateTimeField(blank=False, help_text="Event timestamp", null=False)),
                (
                    "question",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="service_usage_events",
                        to="django_twined.question",
                    ),
                ),
                (
                    "service_revision",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="service_usage_events",
                        to="django_twined.servicerevision",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddConstraint(
            model_name="servicerevision",
            constraint=models.UniqueConstraint(fields=("namespace", "name", "tag"), name="unique_identifier"),
        ),
        migrations.AddField(
            model_name="question",
            name="service_revision",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="questions",
                to="django_twined.servicerevision",
            ),
        ),
    ]
