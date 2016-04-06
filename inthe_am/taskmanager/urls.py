import os

from django.conf import settings
from django.conf.urls import include, patterns, url
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework import routers

from .views import debug_login, TaskFeed
from .viewsets.activity_log import ActivityLogViewSet
from .viewsets.task import (
    TaskViewSet, ical_feed, incoming_trello, incoming_sms,
)
from .viewsets.user import UserViewSet


router = routers.SimpleRouter()
router.register('tasks', TaskViewSet, base_name='task')
router.register('user', UserViewSet, base_name='user')
router.register('activity-logs', ActivityLogViewSet, base_name='activity_log')


def fallback(request):
    # This is sort of a hack; sorry!
    index_template_path = os.path.join(
        settings.BASE_DIR,
        'dist/index.html'
    )
    with open(index_template_path) as index:
        return HttpResponse(index.read())


def view_does_not_exist(request):
    return HttpResponseNotFound()


urlpatterns = patterns(
    '',
    url('^api/v2/', include(router.urls, namespace='api')),
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
    url('^', fallback),
)

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
