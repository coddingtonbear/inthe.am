import shutil
import os
import tempfile

from django.contrib.auth.models import User
from django.test import TestCase

from inthe_am.taskmanager.models import TaskStore


class TaskManagerTest(TestCase):
    def setUp(self):
        self.store_path = tempfile.mkdtemp()

        self.username = 'alpha'
        self.password = '1qaz2wsx'
        self.email = self.username + '@localhost'
        self.user = User.objects.create_user(
            self.username,
            self.email,
            self.password,
        )
        self.store = TaskStore.objects.create(
            user=self.user,
            local_path=self.store_path
        )
        self.store.sync = lambda: None
        self.store._create_git_repo()

        self.store.repository.stage(
            [
                f for f in os.listdir(self.store.repository.path)
                if f != '.git'
            ]
        )
        self.store.autoconfigure_taskd()
        self.store.repository.do_commit("Initial Commit")

    def tearDown(self):
        shutil.rmtree(self.store_path)
