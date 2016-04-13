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
    CONFIG_OVERRIDES = {
        CONFIG_SECTION: {
            'development': 'true',
            'shorten': 'false',
            'inline_link': 'false',
            'legacy_matching': 'false',
            'log.level': 'DEBUG',
        }
    }

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
            for section in self.CONFIG_OVERRIDES:
                section_data = self.CONFIG_OVERRIDES.get(section, {})
                for key, value in section_data.items():
                    config.set(section, key, value)
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

            for option in self.config.options(target):
                if '@oracle' in self.config.get(target, option):
                    raise InvalidBugwarriorConfiguration(
                        "Target '%s' attempts to use @oracle for gathering "
                        "the service's password, but @oracle is not available "
                        "on Inthe.AM." % (
                            target,
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

            self.store.publish_personal_announcement({
                'title': 'Bugwarrior',
                'message': 'Synchronization started...'
            })

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
            self.store.publish_personal_announcement({
                'title': 'Bugwarrior',
                'message': 'Synchronization completed successfully.'
            })
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
            self.store.publish_personal_announcement({
                'type': 'error',
                'title': 'Bugwarrior',
                'message': (
                    'An error was encountered while synchronizing with '
                    'bugwarrior; see your activity log for details.'
                )
            })

        log.finished = timezone.now()
        log.save()

    def __unicode__(self):
        return "Bugwarrior Config for %s" % self.store

    class Meta:
        app_label = 'taskmanager'
