import datetime
import hashlib
import json
import logging
import os
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
    dropbox_path = models.CharField(
        max_length=255,
        blank=True,
    )
    configured = models.BooleanField(default=False)
    dirty = models.BooleanField(default=False)

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
                self.metadata['taskrc']
            )
        return self._client

    @property
    def dropbox(self):
        if not getattr(self, '_dropbox', None):
            db_info = self.user.social_auth.get(provider='dropbox').extra_data
            session = dropbox.session.DropboxSession(
                settings.SOCIAL_AUTH_DROPBOX_KEY,
                settings.SOCIAL_AUTH_DROPBOX_SECRET,
            )
            session.set_token(
                db_info['access_token']['oauth_token'],
                db_info['access_token']['oauth_token_secret'],
            )
            self._dropbox = dropbox.client.DropboxClient(
                session
            )
        return self._dropbox

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

        with open(self.metadata['taskrc'], 'w') as task_rc:
            task_rc.write(
                '# generated an %s UTC\n' % datetime.datetime.utcnow()
            )
            task_rc.write('data.location=%s\n' % self.local_path)

        self.save()

        self.fetch_files_from_dropbox()

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

    def fetch_files_from_dropbox(self):
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
            with dropbox_file:
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
        print files_changed

        for filename in files_changed:
            local_path = os.path.join(self.local_path, filename)
            remote_path = os.path.join(self.dropbox_path, filename)

            with open(local_path, 'rb') as input_file:
                local_hash = hashlib.md5(input_file.read()).hexdigest()
                print '%s --> Dropbox' % local_path
                logger.info(
                    '%s-->Dropbox' % local_path
                )
                new_meta = self.dropbox.put_file(
                    remote_path,
                    input_file,
                    overwrite=True,
                )
                print new_meta
                new_meta['md5'] = local_hash
                metadata['files'][filename] = new_meta

        self.metadata = metadata

    def __unicode__(self):
        return 'Tasks for %s' % self.user
