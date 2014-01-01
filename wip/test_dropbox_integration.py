import os
import unittest

import dropbox

from . import dropbox_integration


class TestDropbox(unittest.TestCase):
    def setUp(self):
        self.access_token = os.environ['DROPBOX_ACCESS_TOKEN']

    def test_find_tasks_in_dropbox(self):
        expected_task_folders = ['/Tasks']

        client = dropbox.client.DropboxClient(self.access_token)
        actual_task_folders = dropbox_integration.find_tasks_in_dropbox(
            client
        )

        self.assertEqual(
            expected_task_folders,
            actual_task_folders,
        )
