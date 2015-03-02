import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from inthe_am.taskmanager.lock import get_lock_redis


logger = logging.getLogger(__name__)


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

    def save(self, *args, **kwargs):
        value = super(TaskStoreActivityLog, self).save(*args, **kwargs)
        if self.silent:
            return value

        try:
            connection = get_lock_redis()
            connection.publish(
                'log:%s:%s' % (
                    'error' if self.error else 'msg',
                    self.store.username,
                ),
                json.dumps(
                    {
                        'md5hash': self.md5hash,
                        'last_seen': self.last_seen,
                        'created': self.created,
                        'error': self.error,
                        'silent': self.silent,
                        'message': self.message,
                        'count': self.count,
                    },
                    cls=DjangoJSONEncoder
                )
            )
        except:
            logger.exception(
                "Error encountered while attempting to "
                "emit pubsub message for received error."
            )

        return value

    class Meta:
        unique_together = ('store', 'md5hash', )
        app_label = 'taskmanager'
