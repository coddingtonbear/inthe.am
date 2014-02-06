from tastypie.api import Api

from django.conf.urls import include, patterns, url

from .api import UserResource, TaskResource, CompletedTaskResource
from .views import home, Status

api = Api(api_name='v1')
api.register(UserResource())
api.register(TaskResource())
api.register(CompletedTaskResource())


urlpatterns = patterns('inthe_am.taskmanager.views',
    url('^api/', include(api.urls)),
    url('^status/', Status.as_view()),
    url('^', home, name='home'),
)
