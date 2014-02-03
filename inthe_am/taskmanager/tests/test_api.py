import copy
import datetime

from django.core.urlresolvers import reverse
from django.utils import dateformat
import pytz
from tastypie.utils.timezone import make_naive

from .base import TaskManagerTest


class TasksApi(TaskManagerTest):
    def setUp(self):
        super(TasksApi, self).setUp()
        self.arbitrary_task_data = {
            'description': 'TEST TASK',
        }
        self.arbitrary_task = self.store.client.task_add(
            **self.arbitrary_task_data
        )

    def format_date(self, date):
        return dateformat.format(make_naive(date), 'r')

    def get_credentials(self):
        return self.create_apikey(
            self.user.username,
            self.user.api_key.key
        )

    def test_get_single_task(self):
        data = self.api_client.get(
            reverse(
                'api_dispatch_detail',
                kwargs={
                    'api_name': 'v1',
                    'resource_name': 'task',
                    'pk': self.arbitrary_task['uuid']
                }
            ),
            authentication=self.get_credentials()
        )
        actual_values = self.deserialize(data)
        expected_values = {
            'project': None,
            'tags': None,
            'due': None,
            'annotations': None,
            'priority': None,
            'start': None,
            'depends': None,
            'status': 'pending',
            'modified': None,
            'scheduled': None,
            'wait': None,
        }
        expected_values.update(self.arbitrary_task_data)
        for k, v in expected_values.items():
            self.assertEqual(
                actual_values[k],
                v,
                k + ' does not match',
            )

    def test_get_all_completed_tasks(self):
        data = self.api_client.get(
            reverse(
                'api_dispatch_list',
                kwargs={
                    'api_name': 'v1',
                    'resource_name': 'completedtask',
                }
            ),
            authentication=self.get_credentials()
        )

        objects = self.deserialize(data)['objects']

        self.assertEqual(len(objects), 0)

        self.api_client.delete(
            reverse(
                'api_dispatch_detail',
                kwargs={
                    'api_name': 'v1',
                    'resource_name': 'task',
                    'pk': self.arbitrary_task['uuid']
                }
            ),
            authentication=self.get_credentials()
        )

        data = self.api_client.get(
            reverse(
                'api_dispatch_list',
                kwargs={
                    'api_name': 'v1',
                    'resource_name': 'completedtask',
                }
            ),
            authentication=self.get_credentials()
        )

        objects = self.deserialize(data)['objects']

        self.assertEqual(len(objects), 1)

    def test_get_all_tasks(self):
        data = self.api_client.get(
            reverse(
                'api_dispatch_list',
                kwargs={
                    'api_name': 'v1',
                    'resource_name': 'task',
                }
            ),
            authentication=self.get_credentials()
        )

        objects = self.deserialize(data)['objects']

        self.assertEqual(len(objects), 1)

    def test_delete_task(self):
        results = self.store.client.load_tasks()
        self.assertEqual(len(results['pending']), 1)
        self.assertEqual(len(results['completed']), 0)

        self.api_client.delete(
            reverse(
                'api_dispatch_detail',
                kwargs={
                    'api_name': 'v1',
                    'resource_name': 'task',
                    'pk': self.arbitrary_task['uuid']
                }
            ),
            authentication=self.get_credentials()
        )

        results = self.store.client.load_tasks()
        self.assertEqual(len(results['pending']), 0)
        self.assertEqual(len(results['completed']), 1)

    def test_create_task(self):
        wait_date = (
            datetime.datetime.now() + datetime.timedelta(days=1)
        ).replace(tzinfo=pytz.timezone('Europe/Moscow'))
        arbitrary_task = {
            'project': 'Arbitrary',
            'description': 'Once upon a time',
            'tags': ['one', 'two'],
            'wait': self.format_date(wait_date)
        }

        data = self.api_client.post(
            reverse(
                'api_dispatch_list',
                kwargs={
                    'api_name': 'v1',
                    'resource_name': 'task',
                }
            ),
            data=arbitrary_task,
            authentication=self.get_credentials()
        )

        actual_task_data = self.deserialize(data)

        for k, v in arbitrary_task.items():
            self.assertEqual(
                actual_task_data[k],
                v,
                k + ' does not match'
            )

    def test_update_task(self):
        updated_task = copy.deepcopy(self.arbitrary_task)
        wait_time = datetime.datetime.now() + datetime.timedelta(hours=72)
        updated_data = {
            'project': 'Alphaville',
            'tags': ['alpha', 'aleph', 'ah'],
            'wait': self.format_date(wait_time)
        }
        updated_task.update(updated_data)

        data = self.api_client.put(
            reverse(
                'api_dispatch_detail',
                kwargs={
                    'api_name': 'v1',
                    'resource_name': 'task',
                    'pk': self.arbitrary_task['uuid']
                }
            ),
            data=updated_task,
            authentication=self.get_credentials()
        )

        actual_task = self.deserialize(data)
        for k, v in updated_data.items():
            if k == 'status':
                # Skip status -- we expect it to change to waiting
                continue
            self.assertEqual(
                actual_task[k],
                v,
                k + ' does not match'
            )
        self.assertEqual(
            actual_task['uuid'],
            self.arbitrary_task['uuid'],
        )
