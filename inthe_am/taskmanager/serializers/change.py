from rest_framework import serializers

from .. import models


class ChangeSerializer(serializers.ModelSerializer):
    source_id = serializers.IntegerField(source="source.pk")
    sourcetype = serializers.CharField(source="source.get_sourcetype_display")
    foreign_id = serializers.CharField(source="source.foreign_id")

    class Meta:
        model = models.Change
        fields = (
            "source_id",
            "sourcetype",
            "foreign_id",
            "task_id",
            "field",
            "data_from",
            "data_to",
            "changed",
        )
