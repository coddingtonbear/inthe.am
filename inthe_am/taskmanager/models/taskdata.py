from __future__ import annotations

import json
import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models


class TaskData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data = JSONField()
    source = models.ForeignKey(
        "taskmanager.ChangeSource",
        related_name="task_datas",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    predecessor = models.ForeignKey(
        "taskmanager.TaskData",
        related_name="successors",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return json.dumps(self.data)
