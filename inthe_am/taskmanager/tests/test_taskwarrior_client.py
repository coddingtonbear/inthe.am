import mock
from taskw.warrior import TaskWarriorBase

from .base import TaskManagerTest
from inthe_am.taskmanager.taskwarrior_client import TaskwarriorClient


class TestTaskwarriorClient(TaskManagerTest):
    def setUp(self):
        TaskWarriorBase.load_config = mock.MagicMock(name='load_config')
        self.tw = TaskwarriorClient(None)
        super(TestTaskwarriorClient, self).setUp()

    def test_get_acceptable_prefix_reject(self):
        unacceptable = 'one'
        self.assertFalse(
            self.tw._get_acceptable_prefix(unacceptable)
        )

    def test_get_acceptable_prefix_accept(self):
        acceptable = 'Due'

        expected = 'due'
        actual = self.tw._get_acceptable_prefix(acceptable)

        self.assertEqual(expected, actual)

    def test_strip_unsafe_args(self):
        args = [
            'rc:one',
            'something to keep: yes',
            'project:alpha',
        ]
        expected = [
            'something to keep: yes',
            'project:alpha',
            '--',
            'rc:one',
        ]
        actual = self.tw._strip_unsafe_args(*args)

        self.assertEqual(expected, actual)
