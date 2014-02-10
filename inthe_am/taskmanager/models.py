import datetime
import json
import logging
import os
import subprocess
import tempfile
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template.loader import render_to_string
from dulwich.repo import Repo
from tastypie.models import create_api_key, ApiKey

from .context_managers import git_checkpoint
from .taskwarrior_client import TaskwarriorClient
from .taskstore_migrations import upgrade as upgrade_taskstore


logger = logging.getLogger(__name__)


class MultipleTaskFoldersFound(Exception):
    pass


class NoTaskFoldersFound(Exception):
    pass


class TaskStore(models.Model):
    DEFAULT_FILENAMES = {
        'key': 'private.key.pem',
        'certificate': 'private.certificate.pem',
    }

    user = models.ForeignKey(User, related_name='task_stores')
    local_path = models.FilePathField(
        path=settings.TASK_STORAGE_PATH,
        allow_files=False,
        allow_folders=True,
        blank=True,
    )
    twilio_auth_token = models.CharField(max_length=32, blank=True)
    taskrc_extras = models.TextField(blank=True)
    configured = models.BooleanField(default=False)

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
    def get_for_user(self, user):
        store, created = TaskStore.objects.get_or_create(
            user=user,
        )
        upgrade_taskstore(store)
        return store

    @property
    def client(self):
        if not getattr(self, '_client', None):
            self._client = TaskwarriorClient(
                self.taskrc.path
            )
        return self._client

    @property
    def api_key(self):
        try:
            return self.user.api_key
        except ObjectDoesNotExist:
            return ApiKey.objects.create(user=self.user)

    def _is_numeric(self, val):
        try:
            float(val)
            return True
        except (ValueError, TypeError):
            return False

    def _get_extra_safely(self, key, val):
        valid_numeric_starts = [
            'urgency.next.coefficient',
            'urgency.blocking.coefficient',
            'urgency.blocked.coefficient',
            'urgency.priority.coefficient',
            'urgency.waiting.coefficient',
            'urgency.active.coefficient',
            'urgency.project.coefficient',
            'urgency.tags.coefficient',
            'urgency.annotations.coefficient',
            'urgency.user.tag',
            'urgency.user.project',
            'urgency.age.coefficient',
            'urgency.age.max',
        ]
        for start in valid_numeric_starts:
            if key.startswith(start) and self._is_numeric(val):
                return True, None
            elif key.startswith(start):
                return False, "Setting '%s' requires a numeric value." % key
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
            temp_extras.write(self.taskrc_extras)
            temp_extras.flush()
            extras = TaskRc(temp_extras.name, read_only=True)

            with open(extras_path, 'w') as applied_extras:
                for key, value in extras.items():
                    safe, message = self._get_extra_safely(key, value)
                    if safe:
                        applied[key] = value
                        applied_extras.write(
                            "%s=%s\n" % (
                                key,
                                value,
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
                self.user.username
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

        self.apply_extras()
        super(TaskStore, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Tasks for %s' % self.user

    #  Git-related methods

    def _create_git_repo(self):
        result = self._simple_git_command('status')
        if result != 0:
            self._simple_git_command('init')
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

    def create_git_checkpoint(
        self, message, function=None,
        args=None, kwargs=None, pre_operation=False
    ):
        self._create_git_repo()
        self._simple_git_command('add', '-A')
        commit_message = render_to_string(
            'git_checkpoint.txt',
            {
                'message': message,
                'function': function,
                'args': args,
                'kwargs': kwargs,
                'preop': pre_operation,
            }
        )
        self._simple_git_command(
            'commit',
            '-m',
            commit_message
        )

    #  Taskd-related methods

    def sync(self):
        with git_checkpoint(self, 'Synchronization'):
            self.client.sync()

    def autoconfigure_taskd(self):
        self.configured = True

        logger.warning(
            '%s just autoconfigured an account!',
            self.user.username,
        )

        # Remove any cached taskrc/taskw clients
        for attr in ('_taskrc', '_client', ):
            try:
                delattr(self, attr)
            except AttributeError:
                pass

        # Create a new user username
        key_proc = subprocess.Popen(
            [
                settings.TASKD_BINARY,
                'add',
                '--data',
                settings.TASKD_DATA,
                'user',
                settings.TASKD_ORG,
                self.user.username,
            ],
            stdout=subprocess.PIPE
        )
        key_proc_output = key_proc.communicate()[0].split('\n')
        taskd_user_key = key_proc_output[0].split(':')[1].strip()

        # Create and write a new private key
        private_key_proc = subprocess.Popen(
            [
                'certtool',
                '--generate-privkey',
            ],
            stdout=subprocess.PIPE
        )
        private_key = private_key_proc.communicate()[0]
        private_key_filename = os.path.join(
            self.local_path,
            self.DEFAULT_FILENAMES['key'],
        )
        with open(private_key_filename, 'w') as out:
            out.write(private_key)

        # Create and write a new public key
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
            stdout=subprocess.PIPE
        )
        cert = cert_proc.communicate()[0]
        cert_filename = os.path.join(
            self.local_path,
            self.DEFAULT_FILENAMES['certificate'],
        )
        with open(cert_filename, 'w') as out:
            out.write(cert)

        # Save these details to the taskrc
        taskd_credentials = '%s/%s/%s' % (
            settings.TASKD_ORG,
            self.user.username,
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

        self.save()
        self.create_git_checkpoint("Local store created")


class Metadata(dict):
    def __init__(self, store, path):
        self.path = path
        self.store = store

        self.config = self._read()

    def _init(self):
        self.config = {
            'files': {
            },
            'taskrc': os.path.join(
                self.store.local_path,
                '.taskrc',
            ),
        }
        self._write()
        return self.config

    def _read(self):
        if not os.path.isfile(self.path):
            return self._init()

        with open(self.path, 'r') as config_file:
            return json.loads(config_file.read())

    def _write(self):
        with open(self.path, 'w') as config_file:
            config_file.write(json.dumps(self.config))

    def items(self):
        return self.config.items()

    def keys(self):
        return self.config.keys()

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, item, value):
        self.config[item] = value
        self._write()

    def __unicode__(self):
        return u'metadata at %s' % self.path

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'REPLACE')


class TaskRc(object):
    def __init__(self, path, read_only=False):
        self.path = path
        self.read_only = read_only
        if not os.path.isfile(self.path):
            self.config, self.includes = {}, []
        else:
            self.config, self.includes = self._read(self.path)

    def _read(self, path):
        config = {}
        includes = []
        with open(path, 'r') as config_file:
            for line in config_file.readlines():
                if line.startswith('#'):
                    continue
                if line.startswith('include '):
                    try:
                        left, right = line.split(' ')
                        if right.strip() not in includes:
                            includes.append(right.strip())
                    except ValueError:
                        pass
                else:
                    try:
                        left, right = line.split('=')
                        key = left.strip()
                        value = right.strip()
                        config[key] = value
                    except ValueError:
                        pass
        return config, includes

    def _write(self, path=None, data=None, includes=None):
        if path is None:
            path = self.path
        if data is None:
            data = self.config
        if includes is None:
            includes = self.includes
        if self.read_only:
            raise AttributeError(
                "This instance is read-only."
            )
        with open(path, 'w') as config:
            config.write(
                '# Generated by taskmanager at %s UTC\n' % (
                    datetime.datetime.utcnow()
                )
            )
            for include in includes:
                config.write(
                    "include %s\n" % (
                        include
                    )
                )
            for key, value in data.items():
                config.write(
                    "%s=%s\n" % (
                        key,
                        value
                    )
                )

    def items(self):
        return self.config.items()

    def keys(self):
        return self.config.keys()

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, item, value):
        self.config[item] = str(value)
        self._write()

    def update(self, value):
        self.config.update(value)
        self._write()

    def add_include(self, item):
        if item not in self.includes:
            self.includes.append(item)
        self._write()

    def __unicode__(self):
        return u'.taskrc at %s' % self.path

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'REPLACE')


models.signals.post_save.connect(create_api_key, sender=User)
