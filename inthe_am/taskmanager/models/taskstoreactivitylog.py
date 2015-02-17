from django.db import models


class TaskStoreActivityLog(models.Model):
    store = models.ForeignKey('TaskStore', related_name='log_entries')
    md5hash = models.CharField(max_length=32)
    last_seen = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    error = models.BooleanField(default=False)
    silent = models.BooleanField(default=False)
    message = models.TextField()
    count = models.IntegerField(default=0)

    def __unicode__(self):
        return self.message.replace('\n', ' ')[0:50]

    class Meta:
        unique_together = ('store', 'md5hash', )
        app_label = 'taskmanager'
