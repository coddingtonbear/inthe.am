from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .. import models
from ..serializers.change import ChangeSerializer


class ChangeViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ChangeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "source__id",
        "source__foreign_id",
        "source__commit_hash",
        "source__sourcetype",
        "field",
        "data_from",
        "data_to",
    ]

    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return models.Change.objects.none()
        return (
            models.Change.objects.select_related("source")
            .filter(
                source__store__user=self.request.user, task_id=self.kwargs["task_id"]
            )
            .order_by("-changed")
        )
