import datetime
import hashlib
import json
import logging
import os
import re
import subprocess
import tempfile
import time
import uuid

from dulwich.repo import Repo
from tastypie.models import ApiKey

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string
from django.utils.timezone import now

from ..context_managers import git_checkpoint
from ..lock import get_debounce_name_for_store, get_lock_redis
from ..tasks import sync_repository, sync_trello_tasks
from ..taskstore_migrations import upgrade as upgrade_taskstore
from ..taskwarrior_client import TaskwarriorClient
from .taskrc import TaskRc
from .metadata import Metadata
from .taskstoreactivitylog import TaskStoreActivityLog


logger = logging.getLogger(__name__)

HEX_COLOR_RE = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')


class TaskStore(models.Model):
    REPLY_ALL = 9
    REPLY_ERROR = 5
    REPLY_NEVER = 0
    REPLY_CHOICES = (
        (REPLY_ALL, 'Reply to all messages', ),
        (REPLY_ERROR, 'Reply only to error messages', ),
        (REPLY_NEVER, 'Do not reply to any incoming text messages', ),
    )

    DEFAULT_FILENAMES = {
        'key': 'private.key.pem',
        'certificate': 'private.certificate.pem',
    }

    user = models.ForeignKey(
        User,
        related_name='task_stores',
        null=True,
        blank=True,
    )
    local_path = models.CharField(
        max_length=255,
        blank=True,
    )

    configured = models.BooleanField(default=False)
    secret_id = models.CharField(blank=True, max_length=36)
    sync_enabled = models.BooleanField(default=True)
    sync_permitted = models.BooleanField(default=True)
    pebble_cards_enabled = models.BooleanField(default=False)
    feed_enabled = models.BooleanField(default=False)

    taskrc_extras = models.TextField(blank=True)

    twilio_auth_token = models.CharField(max_length=32, blank=True)

    trello_auth_token = models.CharField(max_length=32, blank=True)

    sms_whitelist = models.TextField(blank=True)
    sms_arguments = models.TextField(blank=True)
    sms_replies = models.PositiveIntegerField(
        choices=REPLY_CHOICES,
        default=REPLY_ALL
    )

    email_whitelist = models.TextField(blank=True)

    last_synced = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def username(self):
        try:
            return self.user.username
        except:
            return '(None)'

    @property
    def version(self):
        return self.metadata.get('version', 0)

    @version.setter
    def version(self, value):
        self.metadata['version'] = value

    @property
    def metadata_registry(self):
        return os.path.join(
            self.local_path,
            '.meta'
        )

    @property
    def metadata(self):
        if not getattr(self, '_metadata', None):
            self._metadata = Metadata(self, self.metadata_registry)
        return self._metadata

    @property
    def taskrc(self):
        if not getattr(self, '_taskrc', None):
            self._taskrc = TaskRc(self.metadata['taskrc'])
        return self._taskrc

    @property
    def taskd_certificate_status(self):
        results = {}
        certificate_settings = (
            'taskd.certificate',
            'taskd.key',
            'taskd.ca',
        )
        for setting in certificate_settings:
            setting_value = setting.replace('.', '_')
            value = self.taskrc.get(setting, '')
            if not value:
                results[setting_value] = 'No file available'
            elif 'custom' in value:
                results[setting_value] = 'Custom certificate in use'
            else:
                results[setting_value] = 'Standard certificate in use'
        results['taskd_trust'] = self.taskrc.get('taskd.trust', 'no')
        return results

    @property
    def repository(self):
        return Repo(self.local_path)

    @property
    def server_config(self):
        return TaskRc(
            os.path.join(
                settings.TASKD_DATA,
                'config'
            ),
            read_only=True
        )

    @classmethod
    def get_for_user(cls, user):
        store, created = TaskStore.objects.get_or_create(
            user=user,
        )
        upgrade_taskstore(store)
        return store

    @property
    def client(self):
        if not getattr(self, '_client', None):
            self._client = TaskwarriorClient(
                self.taskrc.path,
                config_overrides=settings.TASKWARRIOR_CONFIG_OVERRIDES
            )
        return self._client

    @property
    def api_key(self):
        try:
            return self.user.api_key
        except ObjectDoesNotExist:
            return ApiKey.objects.create(user=self.user)

    @property
    def trello_board(self):
        from .trello_object import TrelloObject

        try:
            return TrelloObject.objects.get(
                store=self,
                type=TrelloObject.BOARD,
            )
        except TrelloObject.DoesNotExist:
            return None

    def _is_numeric(self, val):
        try:
            float(val)
            return True
        except (ValueError, TypeError):
            return False

    def _is_valid_type(self, val):
        if val in ('string', 'numeric', 'date', 'duration'):
            return True
        return False

    def _get_extra_safely(self, key, val):
        valid_patterns = [
            (
                re.compile('^urgency\.[^.]+\.coefficient$'),
                self._is_numeric
            ),
            (
                re.compile('^urgency\.user\.tag\.[^.]+\.coefficient$'),
                self._is_numeric
            ),
            (
                re.compile('^urgency\.user\.project\.[^.]+.coefficient$'),
                self._is_numeric
            ),
            (
                re.compile('^urgency\.age\.max$'),
                self._is_numeric
            ),
            (
                re.compile('^urgency\.uda\.[^.]+\.coefficient$'),
                self._is_numeric
            ),
            (
                re.compile('^uda\.[^.]+\.type$'),
                self._is_valid_type
            ),
            (
                re.compile('^uda\.[^.]+\.label$'),
                lambda x: True  # Accept all strings
            )
        ]
        for pattern, verifier in valid_patterns:
            if pattern.match(key) and verifier(val):
                return True, None
            elif pattern.match(key):
                return False, "Setting '%s' has an invalid value." % key
        return False, "Setting '%s' could not be applied." % key

    def apply_extras(self):
        default_extras_path = os.path.join(
            self.local_path,
            '.taskrc_extras',
        )
        extras_path = self.metadata.get('taskrc_extras', default_extras_path)
        self.metadata['taskrc_extras'] = default_extras_path

        applied = {}
        errored = {}
        self.taskrc.add_include(extras_path)
        with tempfile.NamedTemporaryFile() as temp_extras:
            temp_extras.write(self.taskrc_extras.encode('utf8'))
            temp_extras.flush()
            extras = TaskRc(temp_extras.name, read_only=True)

            with open(extras_path, 'w') as applied_extras:
                for key, value in extras.items():
                    safe, message = self._get_extra_safely(key, value)
                    if safe:
                        applied[key] = value
                        applied_extras.write(
                            "%s=%s\n" % (
                                key.encode('utf8'),
                                value.encode('utf8'),
                            )
                        )
                    else:
                        errored[key] = (value, message)
        return applied, errored

    def save(self, *args, **kwargs):
        # Create the user directory
        if not self.local_path:
            user_tasks = os.path.join(
                settings.TASK_STORAGE_PATH,
                self.username,
            )
            if not os.path.isdir(user_tasks):
                os.mkdir(user_tasks)
            self.local_path = os.path.join(
                user_tasks,
                str(uuid.uuid4())
            )
            if not os.path.isdir(self.local_path):
                os.mkdir(self.local_path)
            with open(os.path.join(self.local_path, '.gitignore'), 'w') as out:
                out.write('.lock\n')
            self.create_git_repository()

        if not self.secret_id:
            self.secret_id = str(uuid.uuid4())

        self.apply_extras()
        super(TaskStore, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Tasks for %s' % self.username

    #  Git-related methods

    def get_changed_task_ids(self, head, start=None):
        uuid_matcher = re.compile(r'uuid:"([0-9a-zA-Z-]+)"')
        if not start:
            start = self.repository.head()
        proc = self._git_command(
            'diff', head, start
        )
        stdout, stderr = proc.communicate()
        changed_tickets = set()
        for raw_line in stdout.split('\n'):
            line = raw_line.strip()
            if not line or line[0] not in ('+', '-'):
                continue
            matched = uuid_matcher.search(line)
            if matched:
                changed_tickets.add(
                    matched.group(1)
                )

        return changed_tickets

    def create_git_repository(self):
        result = self._simple_git_command('status')
        if result != 0:
            self._simple_git_command('init')
            self.create_git_checkpoint('Initial Commit')
            return True
        return False

    def _git_command(self, *args):
        command = [
            'git',
            '--work-tree=%s' % self.local_path,
            '--git-dir=%s' % os.path.join(
                self.local_path,
                '.git'
            )
        ] + list(args)
        return subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def _simple_git_command(self, *args):
        proc = self._git_command(*args)
        stdout, stderr = proc.communicate()
        return proc.returncode

    def git_reset(self, to_sha):
        self._simple_git_command('reset', '--hard', to_sha)

    def create_git_checkpoint(
        self, message, function=None,
        args=None, kwargs=None, pre_operation=False,
        rollback=False, checkpoint_id=None
    ):
        self._simple_git_command('add', '-A')
        commit_message = render_to_string(
            'git_checkpoint.txt',
            {
                'message': message,
                'function': function,
                'args': args,
                'kwargs': kwargs,
                'preop': pre_operation,
                'rollback': rollback,
                'checkpoint_id': checkpoint_id,
            }
        )
        self._simple_git_command(
            'commit',
            '--author',
            'Inthe.AM Git Bot <gitbot@inthe.am>',
            '-m',
            commit_message
        )

    #  Taskd-related methods

    @property
    def using_local_taskd(self):
        if not hasattr(self, '_local_taskd'):
            if self.taskrc['taskd.server'] == settings.TASKD_SERVER:
                self._local_taskd = True
            else:
                self._local_taskd = False
        return self._local_taskd

    @property
    def taskd_data_path(self):
        org, user, uid = (
            self.metadata['generated_taskd_credentials'].split('/')
        )
        return os.path.join(
            settings.TASKD_DATA,
            'orgs',
            org,
            'users',
            uid,
            'tx.data'
        )

    @property
    def sync_uses_default_server(self):
        return self.taskrc.get('taskd.server') == settings.TASKD_SERVER

    def _get_queue_name(self, prefix='local_sync', suffix=None):
        base = '%s.%s' % (
            prefix,
            self.user.username,
        )
        if suffix is not None:
            return base + '.' + suffix
        return base

    def _get_announcement_connection(self):
        if not hasattr(self, '_redis'):
            self._redis = get_lock_redis()

        return self._redis

    def publish_announcement(self, prefix, message):
        connection = self._get_announcement_connection()

        connection.publish(
            self._get_queue_name(prefix=prefix),
            json.dumps(message, cls=DjangoJSONEncoder)
        )

    def sync_trello(self):
        debounce_key = get_debounce_name_for_store(self, 'trello')
        defined_debounce_id = str(time.time())

        client = get_lock_redis()
        client.set(debounce_key, defined_debounce_id)
        sync_trello_tasks.apply_async(
            countdown=5,
            expires=3600,
            args=(self.pk, ),
            kwargs={
                'debounce_id': defined_debounce_id,
            }
        )

    def sync(
        self, function=None, args=None, kwargs=None, async=True, msg=None
    ):
        if not self.sync_enabled or not self.sync_permitted:
            return False
        if not self.sync_uses_default_server:
            self.log_message(
                "Synchronization with other taskd servers is no longer "
                "supported.  Your account has been automatically reconfigured "
                "to synchronize with Inthe.AM's built-in task server."
                "You may need to re-configure your local taskwarrior "
                "instances."
            )
            self.reset_taskd_configuration()
            return True

        client = get_lock_redis()
        debounce_id = kwargs.get('debounce_id') if kwargs else None
        debounce_key = get_debounce_name_for_store(self)

        if async:
            defined_debounce_id = str(time.time())
            client.set(debounce_key, defined_debounce_id)
            sync_repository.apply_async(
                countdown=5,
                expires=3600,
                args=(self.pk, ),
                kwargs={
                    'debounce_id': defined_debounce_id,
                }
            )
        else:
            try:
                expected_debounce_id = client.get(debounce_key)
            except (ValueError, TypeError):
                expected_debounce_id = None
            if (
                expected_debounce_id and debounce_id and
                (float(debounce_id) < float(expected_debounce_id))
            ):
                logger.warning(
                    "Debounce Failed: %s<%s; "
                    "skipping synchronization for %s.",
                    debounce_id,
                    expected_debounce_id,
                    self.pk,
                )
                return
            elif expected_debounce_id and debounce_id:
                client.delete(debounce_key)
                logger.debug(
                    "Debounce Succeeded: %s>=%s for %s.",
                    debounce_id,
                    expected_debounce_id,
                    self.pk,
                )

            checkpoint_msg = 'Synchronization'
            if msg:
                checkpoint_msg = '%s: %s' % (checkpoint_msg, msg)

            start = self.repository.head()
            with git_checkpoint(
                self, checkpoint_msg, function=function,
                args=args, kwargs=kwargs, notify_rollback=False
            ):
                self.client.sync()
                self.last_synced = now()
                self.save()

            head = self.repository.head()
            logger.info(
                'Emitting local_sync pubsub event for %s\'s '
                'task store at %s',
                self.username,
                self.local_path
            )
            self.publish_announcement(
                'local_sync',
                {
                    'username': self.username,
                    'debounce_id': debounce_id,
                    'start': start,
                    'head': head,
                }
            )
            changed_task_ids = self.get_changed_task_ids(head, start=start)
            for task_id in changed_task_ids:
                self.publish_announcement(
                    'changed_task',
                    {
                        'username': self.username,
                        'debounce_id': debounce_id,
                        'start': start,
                        'head': head,
                        'task_id': task_id,
                    },
                )

            if changed_task_ids and self.trello_board:
                self.sync_trello()

        return True

    def reset_taskd_configuration(self):
        self.sync_permitted = False
        self.save()  # Just to make sure we don't sync while this is going on

        self.taskrc.update({
            'taskd.certificate': os.path.join(
                self.local_path,
                self.DEFAULT_FILENAMES['certificate']
            ),
            'taskd.key': os.path.join(
                self.local_path,
                self.DEFAULT_FILENAMES['key']
            ),
            'taskd.ca': self.server_config['ca.cert'],
            'taskd.trust': 'no',
            'taskd.server': settings.TASKD_SERVER,
            'taskd.credentials': self.metadata['generated_taskd_credentials']
        })
        self.generate_new_certificate()
        self.clear_taskserver_data()
        try:
            os.unlink(
                os.path.join(
                    self.local_path,
                    'backlog.data',
                )
            )
        except OSError:
            pass
        self.client.sync(init=True)
        self.sync_permitted = True
        self.save()
        self.log_message("Taskd settings reset to default.")

    def clear_taskserver_data(self):
        try:
            os.rename(
                self.taskd_data_path,
                (
                    self.taskd_data_path +
                    datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                )
            )
        except OSError:
            logger.exception(
                "OSError encountered while removing taskd data."
            )

    def autoconfigure_taskd(self):
        with git_checkpoint(self, 'Autoconfiguration'):
            self.configured = True

            logger.warning(
                '%s just autoconfigured an account!',
                self.username,
            )

            # Remove any cached taskrc/taskw clients
            for attr in ('_taskrc', '_client', ):
                try:
                    delattr(self, attr)
                except AttributeError:
                    pass

            # Create a new user username
            env = os.environ.copy()
            env['TASKDDATA'] = settings.TASKD_DATA

            command = [
                settings.TASKD_BINARY,
                'add',
                'user',
                settings.TASKD_ORG,
                self.username,
            ]
            key_proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            key_proc_output = key_proc.communicate()[0].split('\n')
            taskd_user_key = key_proc_output[0].split(':')[1].strip()

            # Create and write a new private key
            private_key_proc = subprocess.Popen(
                [
                    'certtool',
                    '--generate-privkey',
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            private_key = private_key_proc.communicate()[0]
            private_key_filename = os.path.join(
                self.local_path,
                self.DEFAULT_FILENAMES['key'],
            )
            with open(private_key_filename, 'w') as out:
                out.write(private_key)

        with git_checkpoint(self, 'Save initial taskrc credentials'):
            cert_filename = self.generate_new_certificate()

            # Save these details to the taskrc
            taskd_credentials = '%s/%s/%s' % (
                settings.TASKD_ORG,
                self.username,
                taskd_user_key,
            )
            self.taskrc.update({
                'data.location': self.local_path,
                'taskd.certificate': cert_filename,
                'taskd.key': private_key_filename,
                'taskd.ca': self.server_config['ca.cert'],
                'taskd.server': settings.TASKD_SERVER,
                'taskd.credentials': taskd_credentials
            })
            self.metadata['generated_taskd_credentials'] = taskd_credentials

        with git_checkpoint(self, 'Initial Synchronization'):
            self.save()
            self.client.sync(init=True)

    def generate_new_certificate(self):
        private_key_filename = os.path.join(
            self.local_path,
            self.DEFAULT_FILENAMES['key'],
        )
        cert_filename = self.taskrc.get(
            'taskd.certificate',
            os.path.join(
                self.local_path,
                self.DEFAULT_FILENAMES['certificate'],
            )
        )
        # Create and write a new certificate
        cert_proc = subprocess.Popen(
            [
                'certtool',
                '--generate-certificate',
                '--load-privkey',
                private_key_filename,
                '--load-ca-privkey',
                self.server_config['ca.key'],
                '--load-ca-certificate',
                self.server_config['ca.cert'],
                '--template',
                settings.TASKD_SIGNING_TEMPLATE,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        cert = cert_proc.communicate()[0]

        with open(cert_filename, 'w') as out:
            out.write(cert)
        return cert_filename

    def _log_entry(self, message, error=False, params=None, silent=False):
        if params is None:
            params = []
        message_hash = hashlib.md5(
            self.local_path + message % params
        ).hexdigest()
        instance, created = TaskStoreActivityLog.objects.get_or_create(
            store=self,
            md5hash=message_hash,
            defaults={
                'error': error,
                'silent': silent,
                'message': message % params,
                'count': 0,
            }
        )
        instance.count = instance.count + 1
        instance.last_seen = now()
        instance.save()
        return instance

    def log_message(self, message, *parameters):
        self._log_entry(
            message,
            error=False,
            params=parameters
        )

    def log_error(self, message, *parameters):
        self._log_entry(
            message,
            error=True,
            params=parameters
        )

    def log_silent_error(self, message, *parameters):
        self._log_entry(
            message,
            error=True,
            silent=True,
            params=parameters
        )

    class Meta:
        app_label = 'taskmanager'
