from rest_framework import serializers

from .. import models


class ChangeSourceSerializer(serializers.ModelSerializer):
    sourcetype_name = serializers.CharField(source="get_sourcetype_display")

    class Meta:
        model = models.ChangeSource
        fields = (
            "id",
            "sourcetype",
            "sourcetype_name",
            "created",
            "finished",
            "foreign_id",
        )


class ChangeSerializer(serializers.ModelSerializer):
    source = ChangeSourceSerializer()

    class Meta:
        model = models.Change
        fields = (
            "id",
            "source",
            "task_id",
            "field",
            "data_from",
            "data_to",
            "changed",
        )
