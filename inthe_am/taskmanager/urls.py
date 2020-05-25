import os

from django.conf import settings
from django.conf.urls import include, url
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from rest_framework import routers

from .views import debug_login, TaskFeed, RestHookHandler
from .viewsets.activity_log import ActivityLogViewSet
from .viewsets.task import (
    TaskViewSet, ical_feed, incoming_trello, incoming_sms,
)
from .viewsets.user import UserViewSet


router = routers.SimpleRouter()
router.register('tasks', TaskViewSet, base_name='task')
router.register('user', UserViewSet, base_name='user')
router.register('activity-logs', ActivityLogViewSet, base_name='activity_log')


def unmatched(request):
    return HttpResponseNotFound()


def fallback(request):
    # This will redirect to the root path (which will be served for ember
    # via nginx directly); we'll see the 'path=' parameter and ember will
    # use its internal navigation to route you to the proper path
    return HttpResponseRedirect(
        ''.join([
            reverse("fallback"),
            '?path=',
            request.path,
        ])
    )


def view_does_not_exist(request):
    return HttpResponseNotFound()


urlpatterns = [
    url('^api/v2/', include(router.urls, namespace='api')),
    url('^api/v2/hook/$', RestHookHandler.as_view(), name='rest_hook_list'),
    url(
        '^api/v2/hook/(?P<hook_id>[^/]+)/$',
        RestHookHandler.as_view(),
        name='rest_hook_detail'
    ),
    url(
        r'^api/v[1,2]/task/(?P<username>[\w\d_.-]+)/sms/?$',
        incoming_sms,
        name='incoming_sms'
    ),
    url(
        r'^api/v[1-2]/task/ical/(?P<variant>\w+)/(?P<secret_id>[\w\d_.-]+)/?$',
        ical_feed,
        name='ical_feed'
    ),
    url(
        r'^api/v[1-2]/task/trello/incoming/(?P<secret_id>[\w\d_.-]+)/?$',
        incoming_trello,
        name='incoming_trello'
    ),
    url(
        '^api/v[1-2]/task/feed/(?P<uuid>[^/]+)/',
        TaskFeed(),
        name='feed'
    ),
    url(
        '^api/.*',
        unmatched,
    ),
    url('^', fallback, name='fallback'),
]

if settings.DEBUG:
    # Only enabled for local development as a way to
    # get around using google's authentication
    urlpatterns.insert(
        0,
        url(
            '^debug-login/?',
            debug_login,
            name='debug_login'
        ),
    )
