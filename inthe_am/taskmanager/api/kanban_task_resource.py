import re

from tastypie.utils import trailing_slash
from tastypie import authorization

from django.conf.urls import url
from django.core.exceptions import PermissionDenied

from ..models import KanbanBoard
from .task_resource import TaskResource


class KanbanTaskResource(TaskResource):
    BOARD_ID_RE = re.compile(
        r"/api/v1/kanban/(?P<uuid>[^/]+)/"
    )

    def base_urls(self):
        """ Returns default base URLs.

        Note: this overrides the generic behavior because rather than using
        urls like ``/api/v1/task/<id>/``, we'll instead be using urls like
        ``/api/v1/kanban/<uuid>/<id>`` where <uuid> is the ID of the kanban
        board itself.

        """
        return [
            url(
                r"^$",
                self.wrap_view('dispatch_list'),
                name="api_dispatch_list"
            ),
            url(
                r"^schema%s$" % (trailing_slash(), ),
                self.wrap_view('get_schema'),
                name="api_get_schema"
            ),
            url(
                r"^set/(?P<%s_list>.*?)%s$" % (
                    self._meta.detail_uri_name,
                    trailing_slash(),
                ),
                self.wrap_view('get_multiple'),
                name="api_get_multiple"
            ),
            url(
                r"^(?P<%s>.*?)%s$" % (
                    self._meta.detail_uri_name,
                    trailing_slash(),
                ),
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"
            ),
        ]

    def get_task_store(self, request):
        board = KanbanBoard.objects.get(
            uuid=self.BOARD_ID_RE.search(request.path).group('uuid')
        )
        if not board.user_is_member(request.user):
            raise PermissionDenied()

        return board

    class Meta:
        authorization = authorization.Authorization()
