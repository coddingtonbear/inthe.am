from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .. import models
from ..serializers.activity_log import ActivityLogSerializer


class ActivityLogViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ActivityLogSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return models.TaskStoreActivityLog.objects.none()
        return models.TaskStoreActivityLog.objects.filter(
            store__user=self.request.user
        ).order_by("-last_seen")
