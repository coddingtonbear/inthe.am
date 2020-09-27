from django.db import models


class TaskStoreActivityLog(models.Model):
    store = models.ForeignKey(
        "TaskStore", related_name="log_entries", on_delete=models.CASCADE,
    )
    md5hash = models.CharField(max_length=32)
    last_seen = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    error = models.BooleanField(default=False)
    silent = models.BooleanField(default=False)
    message = models.TextField()
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.message.replace("\n", " ")[0:50]

    def save(self, *args, **kwargs):
        self.store.publish_announcement(
            "log_message",
            {
                "username": self.store.user.username,
                "md5hash": self.md5hash,
                "last_seen": self.last_seen,
                "created": self.created,
                "error": self.error,
                "silent": self.silent,
                "message": self.message,
                "count": self.count,
            },
        )
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = (
            "store",
            "md5hash",
        )
        app_label = "taskmanager"
