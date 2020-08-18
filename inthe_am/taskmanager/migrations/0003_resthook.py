# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("taskmanager", "0002_taskstore_auto_deduplicate"),
    ]

    operations = [
        migrations.CreateModel(
            name="RestHook",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        serialize=False,
                        editable=False,
                        primary_key=True,
                    ),
                ),
                ("event_type", models.CharField(max_length=255)),
                ("target_url", models.URLField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "task_store",
                    models.ForeignKey(
                        related_name="rest_hooks", to="taskmanager.TaskStore"
                    ),
                ),
            ],
        ),
    ]
