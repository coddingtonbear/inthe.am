from ConfigParser import SafeConfigParser
from StringIO import StringIO
import traceback

from bugwarrior.services import aggregate_issues, SERVICES
from django.db import models
from django.utils import timezone

from ..bugwarrior_adapter import synchronize
from ..context_managers import git_checkpoint
from ..exceptions import InvalidBugwarriorConfiguration
from .taskstore import TaskStore


class BugwarriorConfig(models.Model):
    CONFIG_SECTION = 'general'

    store = models.ForeignKey(
        TaskStore,
        related_name='bugwarrior_configs',
    )
    serialized_config = models.TextField()

    enabled = models.BooleanField(default=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def config(self):
        if not hasattr(self, '_config'):
            config = SafeConfigParser()
            config.readfp(StringIO(self.serialized_config))
            self._config = config

        return self._config

    def validate_configuration(self):
        if not self.config.has_section(self.CONFIG_SECTION):
            raise InvalidBugwarriorConfiguration(
                "No '%s' section found." % self.CONFIG_SECTION
            )

        if not self.config.has_option(self.CONFIG_SECTION, 'targets'):
            raise InvalidBugwarriorConfiguration(
                "No 'targets' found in '%s' section." % self.CONFIG_SECTION
            )

        targets = self.config.get(self.CONFIG_SECTION, 'targets')
        targets = filter(
            lambda t: len(t), [t.strip() for t in targets.split(",")]
        )
        if not targets:
            raise InvalidBugwarriorConfiguration(
                "Empty 'targets' found in '%s' section." % self.CONFIG_SECTION
            )

        for target in targets:
            if target not in self.config.sections():
                raise InvalidBugwarriorConfiguration(
                    "Section for target '%s' was not found." % target
                )

            if not self.config.get(target, 'service'):
                raise InvalidBugwarriorConfiguration(
                    "No 'service' in section for target '%s'." % target
                )

            if self.config.get(target, 'service') not in SERVICES:
                raise InvalidBugwarriorConfiguration(
                    "Target '%s' requests service %s, but such a service "
                    "either does not exist or is not available." % (
                        target,
                        self.config.get(target, 'service')
                    )
                )

    def pull_issues(self):
        if not self.enabled:
            return False

        from .bugwarriorconfigrunlog import BugwarriorConfigRunLog
        log = BugwarriorConfigRunLog()
        log.config = self
        log.started = timezone.now()
        log.save()

        self.validate_configuration()

        try:
            issues = aggregate_issues(self.config, self.CONFIG_SECTION)

            with git_checkpoint(self.store, "Running bugwarrior-pull"):
                synchronize(
                    log,
                    issues,
                    self.config,
                    self.CONFIG_SECTION
                )
                self.store.sync()

            self.store.log_message(
                "Bugwarrior tasks were synchronized successfully: %s "
                "(Entry ID: %s)",
                log.output,
                log.pk,
            )
            log.success = True
        except Exception as e:
            log.add_output("Issue synchronization failed: %s." % unicode(e))
            log.stack_trace = traceback.format_exc()
            log.success = False
            self.store.log_error(
                "An error was encountered while synchronizing bugwarrior: "
                "%s (Entry ID: %s)",
                log.error_message,
                log.pk,
            )

        log.finished = timezone.now()
        log.save()

    def __unicode__(self):
        return "Bugwarrior Config for %s" % self.store

    class Meta:
        app_label = 'taskmanager'
