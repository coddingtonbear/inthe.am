from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class UserMetadata(models.Model):
    user = models.ForeignKey(
        User, related_name="metadata", unique=True, on_delete=models.CASCADE
    )
    tos_version = models.IntegerField(default=0)
    tos_accepted = models.DateTimeField(default=None, null=True,)
    privacy_policy_version = models.IntegerField(default=0)
    privacy_policy_accepted = models.DateTimeField(default=None, null=True,)
    colorscheme = models.CharField(default="dark-yellow-green.theme", max_length=255,)

    @property
    def tos_up_to_date(self):
        return self.tos_version == settings.TOS_VERSION

    @property
    def privacy_policy_up_to_date(self):
        return self.privacy_policy_version == settings.PRIVACY_POLICY_VERSION

    @classmethod
    def get_for_user(cls, user):
        meta, created = UserMetadata.objects.get_or_create(user=user)
        return meta

    def __str__(self):
        return self.user.username

    class Meta:
        app_label = "taskmanager"
