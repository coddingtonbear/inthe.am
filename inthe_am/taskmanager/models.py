import datetime
import json
import logging
import os
import subprocess
import uuid

from taskw import TaskWarriorExperimental

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


logger = logging.getLogger(__name__)


class MultipleTaskFoldersFound(Exception):
    pass


class NoTaskFoldersFound(Exception):
    pass


class TaskStore(models.Model):
    user = models.ForeignKey(User, related_name='task_stores')
    local_path = models.FilePathField(
        path=settings.TASK_STORAGE_PATH,
        allow_files=False,
        allow_folders=True,
        blank=True,
    )
    taskd_user_key = models.CharField(
        max_length=36,
        blank=True,
    )
    certificate_path = models.FilePathField(
        path=settings.TASK_STORAGE_PATH,
        allow_files=False,
        allow_folders=True,
        blank=True,
    )
    key_path = models.FilePathField(
        path=settings.TASK_STORAGE_PATH,
        allow_files=False,
        allow_folders=True,
        blank=True,
    )
    configured = models.BooleanField(default=False)
    dirty = models.BooleanField(default=False)

    @property
    def metadata_registry(self):
        return os.path.join(
            self.local_path,
            '.meta'
        )

    @property
    def metadata(self):
        if os.path.exists(self.metadata_registry):
            with open(self.metadata_registry, 'r') as m:
                return json.loads(m.read())
        else:
            return {
                'files': {
                },
                'taskrc': os.path.join(
                    self.local_path,
                    '.taskrc',
                )
            }

    @metadata.setter
    def metadata(self, data):
        with open(self.metadata_registry, 'w') as m:
            m.write(
                json.dumps(data)
            )

    @property
    def taskrc(self):
        if not getattr(self, '_taskrc', None):
            self._taskrc = TaskRc(self.metadata['taskrc'])
        return self._taskrc

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
        return store

    @property
    def client(self):
        if not getattr(self, '_client', None):
            self._client = TaskWarriorExperimental(
                self.taskrc.path
            )
        return self._client

    def __unicode__(self):
        return 'Tasks for %s' % self.user

    #  Taskd-related methods

    def sync(self):
        self.client.sync()

    def autoconfigure_taskd(self):
        self.configured = True

        for attr in ('_taskrc', '_client', ):
            try:
                delattr(self, attr)
            except AttributeError:
                pass

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
        os.mkdir(self.local_path)

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
        self.taskd_user_key = key_proc_output[0].split(':')[1].strip()

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
            'private.key.pem',
        )
        with open(private_key_filename, 'w') as out:
            out.write(private_key)
        self.key_path = private_key_filename

        cert_proc = subprocess.Popen(
            [
                'certtool',
                '--generate-certificate',
                '--load-privkey',
                self.key_path,
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
            'private.crt.pem',
        )
        with open(cert_filename, 'w') as out:
            out.write(cert)
        self.certificate_path = cert_filename

        self.taskrc.update({
            'data.location': self.local_path,
            'taskd.certificate': self.certificate_path,
            'taskd.key': self.key_path,
            'taskd.ca': self.server_config['ca.cert'],
            'taskd.server': settings.TASKD_SERVER,
            'taskd.credentials': (
                '%s/%s/%s' % (
                    settings.TASKD_ORG,
                    self.user.username,
                    self.taskd_user_key,
                )
            )
        })

        self.save()


class TaskRc(object):
    def __init__(self, path, read_only=False):
        self.path = path
        self.read_only = read_only
        if not os.path.isfile(self.path):
            self.config = {}
        else:
            self.config = self._read(self.path)

    def _read(self, path):
        out = {}
        with open(path, 'r') as config:
            for line in config.readlines():
                if line.startswith('#'):
                    continue
                left, right = line.split('=')
                key = left.strip()
                value = right.strip()
                out[key] = value
        return out

    def _write(self, path, data):
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
            for key, value in data.items():
                config.write(
                    "%s=%s\n" % (
                        key,
                        value
                    )
                )

    def keys(self):
        return self.config.keys()

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, item, value):
        self.config[item] = str(value)
        self._write(self.path, self.config)

    def update(self, value):
        self.config.update(value)
        self._write(self.path, self.config)

    def __unicode__(self):
        return u'.taskrc at %s' % self.path

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'REPLACE')
