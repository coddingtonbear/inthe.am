from .base import TaskManagerTest


class GetTasks(TaskManagerTest):
    def test_add_task(self):
        self.store.client.task_add("Test")

        self.assertEqual(
            len(self.store.client.load_tasks()['pending']),
            1,
        )

    def test_delete_task(self):
        self.store.client.task_add("Test")
        task = self.store.client.load_tasks()['pending'][0]

        self.store.client.task_delete(uuid=task['uuid'])

        self.assertEqual(
            len(self.store.client.load_tasks()['pending']),
            0,
        )

    def test_done_task(self):
        self.store.client.task_add("Test")
        task = self.store.client.load_tasks()['pending'][0]

        self.store.client.task_done(uuid=task['uuid'])

        self.assertEqual(
            len(self.store.client.load_tasks()['pending']),
            0,
        )
        self.assertEqual(
            len(self.store.client.load_tasks()['completed']),
            1,
        )
