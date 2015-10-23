import datetime

from django.db import models
from django.utils.timezone import now


class TaskStoreActivity(models.Model):
    store = models.ForeignKey('TaskStore', related_name='syncs')
    activity = models.CharField(max_length=255)

    error = models.BooleanField(default=True)
    message = models.TextField()

    duration_seconds = models.PositiveIntegerField()

    updated = models.DateTimeField(auto_now=True)
    started = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.started:
            self.started = (
                now() - datetime.timedelta(seconds=self.duration_seconds)
            )
        super(TaskStoreActivity, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%ss sync of %s" % (
            self.duration_seconds,
            self.store,
        )

    class Meta:
        app_label = 'taskmanager'
