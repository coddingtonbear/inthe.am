from django.conf import settings
from django.conf.urls import include, url
from django.template.response import TemplateResponse
from django.http import HttpResponseNotFound
from rest_framework import routers


from .views import debug_login, TaskFeed, RestHookHandler
from .viewsets.activity_log import ActivityLogViewSet
from .viewsets.change import ChangeViewSet
from .viewsets.task import (
    TaskViewSet,
    ical_feed,
    incoming_trello,
    incoming_sms,
)
from .viewsets.user import UserViewSet


router = routers.SimpleRouter()
router.register("tasks", TaskViewSet, basename="task")
router.register("user", UserViewSet, basename="user")
router.register("activity-logs", ActivityLogViewSet, basename="activity_log")
router.register("changes", ChangeViewSet, basename="change")


def unmatched(request):
    return HttpResponseNotFound()


def serve_ui(request):
    return TemplateResponse(request, "serve_ui.html")


def view_does_not_exist(request):
    return HttpResponseNotFound()


urlpatterns = [
    url("^api/v2/", include(router.urls, namespace="api")),
    url("^api/v2/hook/$", RestHookHandler.as_view(), name="rest_hook_list"),
    url(
        "^api/v2/hook/(?P<hook_id>[^/]+)/$",
        RestHookHandler.as_view(),
        name="rest_hook_detail",
    ),
    url(
        r"^api/v[1,2]/task/(?P<username>[\w\d_.-]+)/sms/?$",
        incoming_sms,
        name="incoming_sms",
    ),
    url(
        r"^api/v[1-2]/task/ical/(?P<variant>\w+)/(?P<secret_id>[\w\d_.-]+)/?$",
        ical_feed,
        name="ical_feed",
    ),
    url(
        r"^api/v[1-2]/task/trello/incoming/(?P<secret_id>[\w\d_.-]+)/?$",
        incoming_trello,
        name="incoming_trello",
    ),
    url("^api/v[1-2]/task/feed/(?P<uuid>[^/]+)/", TaskFeed(), name="feed"),
    url(
        "^api/.*",
        unmatched,
    ),
    url("^", serve_ui, name="serve_ui"),
]

if settings.DEBUG:
    # Only enabled for local development as a way to
    # get around using google's authentication
    urlpatterns.insert(
        0,
        url("^debug-login/?", debug_login, name="debug_login"),
    )
