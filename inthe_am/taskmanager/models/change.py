from __future__ import annotations

import json
from typing import Any

from django.db import models

from .changesource import ChangeSource


class Change(models.Model):
    source = models.ForeignKey(
        ChangeSource,
        related_name="changes",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    task_id = models.UUIDField()

    field = models.CharField(max_length=255)
    data_from = models.TextField()
    data_to = models.TextField()

    changed = models.DateTimeField(auto_now=True)

    @classmethod
    def record_changes(
        cls, source: ChangeSource, task_id: str, field: str, original: Any, final: Any
    ) -> Change:
        return Change.objects.create(
            source=source,
            task_id=task_id,
            field=field,
            data_from=json.dumps(original, default=str),
            data_to=json.dumps(final, default=str),
        )

    def __str__(self):
        return "Task {task} field {field} changed from {data_from} to {data_to}".format(
            task=self.task_id,
            field=self.field,
            data_from=self.data_from,
            data_to=self.data_to,
        )
