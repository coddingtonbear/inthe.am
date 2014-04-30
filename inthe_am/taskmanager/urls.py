from tastypie.api import Api

from django.conf import settings
from django.conf.urls import include, patterns, url

from .api import (
    UserResource, TaskResource, CompletedTaskResource,
    ActivityLogResource
)
from .views import debug_login, home, Status, TaskFeed

api = Api(api_name='v1')
api.register(UserResource())
api.register(TaskResource())
api.register(CompletedTaskResource())
api.register(ActivityLogResource())


urlpatterns = patterns(
    '',
    url('^api/v1/task/feed/(?P<uuid>[^/]+)/', TaskFeed(), name='feed'),
    url('^api/', include(api.urls)),
    url('^status/', Status.as_view(), name='status'),
    url('^', home, name='home'),
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
