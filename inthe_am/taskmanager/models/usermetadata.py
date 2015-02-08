from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class UserMetadata(models.Model):
    user = models.ForeignKey(
        User,
        related_name='metadata',
        unique=True,
    )
    tos_version = models.IntegerField(default=0)
    tos_accepted = models.DateTimeField(
        default=None,
        null=True,
    )
    colorscheme = models.CharField(
        default='dark-yellow-green.theme',
        max_length=255,
    )

    @property
    def tos_up_to_date(self):
        return self.tos_version == settings.TOS_VERSION

    @classmethod
    def get_for_user(cls, user):
        meta, created = UserMetadata.objects.get_or_create(
            user=user
        )
        return meta

    def __unicode__(self):
        return self.user.username

    class Meta:
        app_label = 'taskmanager'
