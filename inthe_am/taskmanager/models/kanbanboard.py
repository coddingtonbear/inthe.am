import uuid

from django.contrib.auth.models import User
from django.db import models

from .taskstore import TaskStore


class KanbanBoard(TaskStore):
    name = models.CharField(max_length=255)
    uuid = models.CharField(max_length=36, blank=True, db_index=True)
    column_names = models.TextField(default='Ready|Doing|Done')

    def user_is_owner(self, user):
        from .kanbanmembership import KanbanMembership
        return KanbanMembership.objects.user_is_owner(self, user)

    def user_is_member(self, user):
        from .kanbanmembership import KanbanMembership
        return KanbanMembership.objects.user_is_member(self, user)

    def sync_outgoing(self):
        kanban_assigned_tasks = self.store.filter_tasks({
            'intheamkanbanassignee.not': '',
        })
        for kanban_task in kanban_assigned_tasks:
            task_id = kanban_task['uuid']
            kanban_task['intheamkanbanboarduuid'] = uuid.UUID(self.uuid)
            kanban_task['intheamkanbantaskuuid'] = task_id
            del kanban_task['uuid']
            assignee_email = kanban_task['intheamkanbanassignee']

            # Check if the assigned user exists:
            try:
                assignee = User.objects.get(
                    email=assignee_email
                )
            except User.DoesNotExist:
                self.log_error(
                    "User %s does not exist; clearing assignee.",
                    assignee_email,
                )
                kanban_task['intheamkanbanassignee'] = ''
                self.store.task_update(kanban_task)
                continue

            # Check if the assignee is a member
            if not self.user_is_member(assignee):
                self.log_error(
                    'User %s is not a member of this kanban board.',
                    assignee,
                )
                continue

            # Find an existing task in the assignee's task list
            assignee_store = TaskStore.get_for_user(assignee)
            existing_tasks = assignee_store.client.filter_tasks({
                'intheamkanbantaskuuid': task_id
            })
            if existing_tasks:
                existing_task_uuid = existing_tasks[0]['uuid']
                # Update the kanban task's UUID to match the user's
                # task; this will make us overwrite
                kanban_task['uuid'] = existing_task_uuid
                assignee_store.client.task_update(kanban_task)
            else:
                # Create a new task in the user's board
                assignee_store.client.task_add(**kanban_task)

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
        super(KanbanBoard, self).save(*args, **kwargs)

    class Meta:
        app_label = 'taskmanager'
