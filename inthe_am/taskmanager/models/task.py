from __future__ import annotations

import uuid

from django.db import models, transaction

from .changesource import ChangeSource
from .taskstore import TaskStore
from .taskdata import TaskData
from ..exceptions import InvalidTaskwarriorConfiguration


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        "taskmanager.TaskStore",
        related_name="tasks",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    task_id = models.UUIDField()
    latest = models.ForeignKey(
        "taskmanager.TaskData", null=False, blank=False, on_delete=models.CASCADE
    )

    @classmethod
    def record_change(cls, store: TaskStore, change_source: ChangeSource, data: dict):
        with transaction.atomic():
            task_data = TaskData()
            task_data.source = change_source
            task_data.data = data

            try:
                task = cls.objects.get(
                    store=store,
                    task_id=data["uuid"],
                )
                if not task.latest or task.latest.data != data:
                    if task.latest:
                        task_data.predecessor = task.latest
                    task_data.save()
                    task.latest = task_data
                    task.save()
            except cls.DoesNotExist:
                task_data.save()
                task = cls.objects.create(
                    store=store,
                    task_id=data["uuid"],
                    latest=task_data,
                )

    @classmethod
    def backfill_task_records(cls, store: TaskStore):
        try:
            with transaction.atomic():
                source = ChangeSource.objects.create(
                    store=store,
                    sourcetype=ChangeSource.SOURCETYPE_BACKFILL,
                    commit_hash=store.repository.head().decode("utf-8"),
                )

                for task in store.client.filter_tasks({}):
                    cls.record_change(
                        store,
                        source,
                        data=task.serialized(),
                    )
        except InvalidTaskwarriorConfiguration:
            # This happens if the user doesn't have an account yet!
            pass

    def __str__(self):
        return f"Task {self.task_id} for {self.store}"
