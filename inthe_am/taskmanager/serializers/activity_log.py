from rest_framework import serializers

from .. import models


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaskStoreActivityLog
        fields = (
            "id",
            "store",
            "md5hash",
            "last_seen",
            "created",
            "error",
            "silent",
            "message",
            "count",
        )
