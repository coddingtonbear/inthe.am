import datetime

from jsonfield import JSONField
import statistics

from django.db import models
from django.utils.timezone import now


class TaskStoreActivity(models.Model):
    store = models.ForeignKey('TaskStore', related_name='syncs')
    activity = models.CharField(max_length=255)
    metadata_version = models.CharField(max_length=10, default='v2')

    message = models.TextField(blank=True)
    metadata = JSONField(null=True, blank=True)

    duration_seconds = models.FloatField(null=True)

    updated = models.DateTimeField(auto_now=True)
    started = models.DateTimeField(auto_now_add=True)

    def add_message_line(self, message):
        message = message.strip()
        self.message = self.message + message + '\n'

    def handle_metadata_message(self, variant, *args, **kwargs):
        metadata = self.metadata

        if variant == 'taskwarrior.execute':
            if 'taskwarrior' not in metadata:
                metadata['taskwarrior'] = {}
            if 'execute' not in metadata['taskwarrior']:
                metadata['taskwarrior']['execute'] = []
            metadata['taskwarrior']['execute'].append(
                args[0]
            )

        all_durations = [
            v['duration'] for v in metadata['taskwarrior']['execute']
        ]
        metadata['taskwarrior']['statistics'] = {
            'max': max(all_durations),
            'min': min(all_durations),
            'stddev': statistics.stdev(all_durations),
            'mean': statistics.mean(all_durations),
        }

        self.metadata = metadata

    def save(self, *args, **kwargs):
        if not self.started and self.duration_seconds:
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
