import datetime
import uuid

from django.db import models


class ChangeSource(models.Model):
    SOURCETYPE_DIRECT = 1
    SOURCETYPE_SYNC = 2
    SOURCETYPE_REVERT = 3
    SOURCETYPE_DEDUPLICATE = 4
    SOURCETYPE_GARBAGE_COLLECTION = 5
    SOURCETYPE_AUTOCONFIGURATION = 6

    SOURCETYPE_MAIL = 20
    SOURCETYPE_TRELLO_OUTGOING = 21
    SOURCETYPE_TRELLO_INCOMING = 22
    SOURCETYPE_TRELLO_RECONCILIATION = 23
    SOURCETYPE_TRELLO_RESET = 23
    SOURCETYPE_SMS = 25

    SOURCETYPE_CHOICES = (
        (SOURCETYPE_DIRECT, "Direct/API"),
        (SOURCETYPE_SYNC, "Sync"),
        (SOURCETYPE_REVERT, "Revert"),
        (SOURCETYPE_DEDUPLICATE, "Deduplication"),
        (SOURCETYPE_GARBAGE_COLLECTION, "Garbage Collection"),
        (SOURCETYPE_AUTOCONFIGURATION, "Autoconfiguration"),
        (SOURCETYPE_MAIL, "Incoming E-mail"),
        (SOURCETYPE_SMS, "Incoming SMS"),
        (SOURCETYPE_TRELLO_OUTGOING, "Trello (Outgoing)"),
        (SOURCETYPE_TRELLO_INCOMING, "Trello (Incoming)"),
        (SOURCETYPE_TRELLO_RECONCILIATION, "Trello (Reconciliation)"),
        (SOURCETYPE_TRELLO_RESET, "Trello (Reset)"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sourcetype = models.PositiveSmallIntegerField(
        choices=SOURCETYPE_CHOICES,
    )
    store = models.ForeignKey(
        "taskmanager.TaskStore",
        related_name="changes",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    foreign_id = models.CharField(max_length=255, blank=True, null=True)

    created = models.DateTimeField(auto_now=True)
    finished = models.DateTimeField(null=True, blank=True)

    def mark_finished(self):
        self.finished = datetime.datetime.now()

    def __str__(self):
        return "{type} ({id})".format(
            type=self.get_sourcetype_display(),
            id=self.foreign_id,
        )

    class Meta:
        ordering = ["-created"]
