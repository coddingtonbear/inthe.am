import datetime
import hashlib
import json
import logging
import os
import subprocess
import uuid

import dropbox
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
    dropbox_path = models.CharField(
        max_length=255,
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
                'add'
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
                settings.TASKD_PRIVATE_KEY,
                '--load-ca-certificate',
                settings.TASKD_CERTIFICATE,
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

    #  Dropbox-related methods

    @property
    def dropbox(self):
        if not getattr(self, '_dropbox', None):
            usa = self.user.social_auth.get(provider='dropbox-oauth2')
            self._dropbox = dropbox.client.DropboxClient(
                usa.extra_data['access_token']
            )
            self._dropbox.session.root = 'dropbox'
        return self._dropbox

    def find_dropbox_folders(self):
        match_path = []
        matched_files = self.dropbox.search('/', 'pending.data')
        for match in matched_files:
            if os.path.basename(match['path']) == 'pending.data':
                dir_name = os.path.dirname(match['path'])
                if dir_name not in match_path:
                    match_path.append(dir_name)
        return match_path

    def autoconfigure_dropbox(self):
        dropbox_folders = self.find_dropbox_folders()
        if len(dropbox_folders) < 1:
            raise NoTaskFoldersFound()
        elif len(dropbox_folders) > 1:
            raise MultipleTaskFoldersFound()

        self.configure_dropbox(dropbox_folders[0])

    def configure_dropbox(self, path):
        self.dropbox_path = path
        self.configured = True
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

        self.taskrc['data.location'] = self.local_path

        self.save()

        self.download_files_from_dropbox()

    def find_changed_files_in_dropbox(self):
        needs_update = []
        task_files = [
            'pending.data',
            'undo.data',
            'backlog.data',
            'completed.data',
        ]
        for filename in task_files:
            file_metadata = self.dropbox.metadata(
                os.path.join(self.dropbox_path, filename)
            )
            local_version = self.metadata['files'].get(filename, {}).get('revision', -1)
            remote_version = file_metadata['revision']

            if local_version != remote_version:
                needs_update.append(filename)

        return needs_update

    def find_changed_files_locally(self):
        needs_update = []
        metadata = self.metadata

        for filename, file_meta in metadata['files'].items():
            local_path = os.path.join(self.local_path, filename)

            with open(local_path, 'r') as input_file:
                local_hash = hashlib.md5(input_file.read()).hexdigest()

                if local_hash != metadata['files'][filename]['md5']:
                    needs_update.append(filename)

        return needs_update

    def download_files_from_dropbox(self):
        files_changed = self.find_changed_files_in_dropbox()
        metadata = self.metadata
        changed = []

        for filename in files_changed:
            dropbox_file, file_meta = self.dropbox.get_file_and_metadata(
                os.path.join(self.dropbox_path, filename)
            )
            logger.info(
                'Dropbox-->%s' % filename
            )
            with open(os.path.join(self.local_path, filename), 'w') as out:
                contents = dropbox_file.read()
                out.write(contents)
                file_meta['md5'] = hashlib.md5(contents).hexdigest()
                changed.append(
                    filename
                )
            metadata['files'][filename] = file_meta
        self.metadata = metadata
        return changed

    def upload_files_to_dropbox(self):
        metadata = self.metadata

        files_changed = self.find_changed_files_locally()

        for filename in files_changed:
            local_path = os.path.join(self.local_path, filename)
            remote_path = os.path.join(
                '/dropbox',
                self.dropbox_path,
                filename
            )

            with open(local_path, 'rb') as input_file:
                local_hash = hashlib.md5(input_file.read()).hexdigest()
                logger.info(
                    '%s-->Dropbox' % local_path
                )
                input_file.seek(0)
                new_meta = self.dropbox.put_file(
                    remote_path,
                    input_file,
                    overwrite=True,
                )
                new_meta['md5'] = local_hash
                metadata['files'][filename] = new_meta

        self.metadata = metadata


class TaskRc(object):
    def __init__(self, path):
        self.path = path
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

    def _write(self, path):
        with open(path, 'w') as config:
            config.write(
                '# Generated by taskmanager at %s UTC\n' % (
                    datetime.datetime.utcnow()
                )
            )
            for key, value in config.items():
                config.write(
                    "%k=%v\n" % (
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
        self._write(self.path)

    def update(self, value):
        self.config.update(value)
        self._write(self.path)

    def __unicode__(self):
        return u'.taskrc at %s' % self.path

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'REPLACE')
