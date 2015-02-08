import uuid

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

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
        super(KanbanBoard, self).save(*args, **kwargs)

    class Meta:
        app_label = 'taskmanager'
