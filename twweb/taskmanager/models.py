from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class TaskStore(models.Model):
    user = models.ForeignKey(User, related_name='task_stores')
    local_path = models.FilePathField(
        path=settings.TASK_STORAGE_PATH,
        allow_files=False,
        allow_folders=True,
    )
    dropbox_path = models.CharField(
        max_length=255,
    )
    dirty = models.BooleanField(default=False)

    def __unicode__(self):
        return 'Tasks for %s' % self.user
