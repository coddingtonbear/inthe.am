from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .. import models
from ..serializers.change import ChangeSerializer


class ChangeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ChangeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["task_id", "field", "data_from", "data_to"]

    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return models.Change.objects.none()
        return models.Change.objects.filter(
            source__store__user=self.request.user
        ).order_by("-changed")
