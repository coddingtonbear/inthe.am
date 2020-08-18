from django.db import models
from django.utils.timezone import now


class CurrentAnnouncementsManager(models.Manager):
    def get_queryset(self):
        return (
            super(CurrentAnnouncementsManager, self)
            .get_queryset()
            .filter(starts__lt=now(), expires__gt=now())
        )


class Announcement(models.Model):
    CATEGORY_ERROR = "error"
    CATEGORY_INFO = "notice"
    CATEGORY_WARNING = "warning"
    CATEGORIES = (
        (CATEGORY_ERROR, "Error",),
        (CATEGORY_INFO, "Info",),
        (CATEGORY_WARNING, "Warning",),
    )

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=10, choices=CATEGORIES)
    duration = models.PositiveIntegerField(default=60 * 5, help_text="In seconds")
    message = models.TextField()
    starts = models.DateTimeField()
    expires = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    current = CurrentAnnouncementsManager()

    def __str__(self):
        return self.title

    class Meta:
        app_label = "taskmanager"
