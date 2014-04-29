from tastypie.api import Api

from django.conf.urls import include, patterns, url

from .api import (
    UserResource, TaskResource, CompletedTaskResource,
    ActivityLogResource
)
from .views import home, Status, TaskFeed

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
