# Generated by Django 3.2.23 on 2024-02-06 11:12

import uuid

from django.db import migrations, models
import django.db.models.deletion

import django_twined.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("django_twined", "0013_alter_serviceusageevent_question"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConcreteSynchronisedDatastore",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("a_string_tag", models.CharField(blank=True, help_text="A string tag", max_length=32)),
                (
                    "a_decimal_tag",
                    models.DecimalField(decimal_places=6, help_text="A decimal number tag", max_digits=10),
                ),
                (
                    "file",
                    django_twined.fields.DatafileObjectField(
                        help_text="Upload a data file which will have Octue metadata on it",
                        store_key="django-twined-concrete-store",
                        upload_to="",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="QuestionWithValuesDatabaseStorage",
            fields=[
                (
                    "question_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="django_twined.question",
                    ),
                ),
                ("input_values", django_twined.fields.ValuesField(blank=True, default=dict, help_text="Values data")),
                ("apple_name", models.CharField(default="macintosh", help_text="Apple name", max_length=32)),
                ("banana_name", models.CharField(default="chiquita", help_text="Banana name", max_length=32)),
            ],
            bases=("django_twined.question",),
        ),
    ]
