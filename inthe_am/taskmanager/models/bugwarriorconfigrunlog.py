from django.db import models

from .bugwarriorconfig import BugwarriorConfig


class BugwarriorConfigRunLog(models.Model):
    config = models.ForeignKey(
        BugwarriorConfig,
        related_name='run_logs',
    )
    success = models.BooleanField(default=False)
    output = models.TextField()
    stack_trace = models.TextField()

    started = models.DateTimeField()
    finished = models.DateTimeField(null=True)

    def add_output(self, new):
        lines = [line for line in self.output.split('\n') if line]
        lines.append(new)

        self.output = '\n'.join(lines)
        self.save()

    def __unicode__(self):
        if self.success:
            category = 'Successful'
        else:
            category = 'Failed'

        return u"{category} bugwarrior-pull run of {config}".format(
            category=category,
            config=self.config
        )

    class Meta:
        app_label = 'taskmanager'
