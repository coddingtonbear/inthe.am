import uuid

from django.db import models

from .taskstore import TaskStore
from ..tasks import send_rest_hook_message


class RestHook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    task_store = models.ForeignKey(
        TaskStore, related_name="rest_hooks", on_delete=models.CASCADE,
    )
    event_type = models.CharField(max_length=255)
    target_url = models.URLField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def send_message(self, task_id):
        send_rest_hook_message.apply_async(
            kwargs={"rest_hook_id": self.id, "task_id": task_id,}
        )

    def __str__(self):
        return f"{self.task_store} ({self.event_type}) --> {self.target_url}"
