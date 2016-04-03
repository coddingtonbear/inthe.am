from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .. import models
from ..serializers.activity_log import ActivityLogSerializer


class ActivityLogViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = ActivityLogSerializer

    def get_queryset(self):
        return models.TaskStoreActivityLog.objects.filter(
            store__user=self.request.user
        ).order_by('-last_seen')
