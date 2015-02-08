import uuid

from django.core.exceptions import ObjectDoesNotExist
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

    def get_task_store_by_email(self, email):
        from .kanbanmembership import KanbanMembership

        matching_assignee = KanbanMembership.objects.members_of(self).get(
            member__email=email
        )
        return TaskStore.get_for_user(matching_assignee.member)

    def sync_outgoing(self):
        kanban_assigned_tasks = self.client.filter_tasks({
            'intheamkanbanassignee.not': '',
        })
        for kanban_task in kanban_assigned_tasks:
            task_id = kanban_task['uuid']
            kanban_task['intheamkanbanboarduuid'] = uuid.UUID(self.uuid)
            kanban_task['intheamkanbantaskuuid'] = task_id
            assignee_email = kanban_task['intheamkanbanassignee']

            # Check if the assigned user exists:
            try:
                assignee_store = self.get_task_store_by_email(
                    assignee_email
                )
            except ObjectDoesNotExist:
                self.log_error(
                    "Task store for %s could not be found; clearing assignee.",
                    assignee_email,
                )
                kanban_task['intheamkanbanassignee'] = ''
                self.client.task_update(kanban_task)
                continue

            # We must wait until after we've found an assignee; we might've
            # needed to update the task above.
            del kanban_task['uuid']

            # Find an existing task in the assignee's task list
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
