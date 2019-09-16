import os

from django.db import models

from .taskstore import TaskStore


def get_attachment_path(instance, filename):
    return os.path.join(
        'attachments',
        instance.store.username,
        instance.task_id,
        filename,
    )


class TaskAttachment(models.Model):
    store = models.ForeignKey(
        TaskStore,
        related_name='attachments',
        on_delete=models.CASCADE,
    )
    task_id = models.CharField(max_length=36)
    name = models.CharField(max_length=256)
    size = models.PositiveIntegerField()
    document = models.FileField(upload_to=get_attachment_path)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u"%s: %s (%s MB)" % (
            self.task_id,
            self.name,
            round(float(self.size) / 2**20, 1)
        )

    class Meta:
        app_label = 'taskmanager'
