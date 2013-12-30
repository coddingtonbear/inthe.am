import os

import unittest

from . import dropbox


class TestDropbox(unittest.TestCase):
    def setUp(self):
        self.access_token = os.environ['DROPBOX_ACCESS_TOKEN']

    def test_find_tasks_in_dropbox(self):
        expected_task_folders = ['/Task']

        actual_task_folders = dropbox.find_tasks_in_dropbox(self.access_token)

        self.assertEqual(
            expected_task_folders,
            actual_task_folders,
        )
