from tastypie.api import Api

from django.conf.urls import include, patterns, url

from .api import UserResource, TaskResource, CompletedTaskResource

api = Api(api_name='v1')
api.register(UserResource())
api.register(TaskResource())
api.register(CompletedTaskResource())


urlpatterns = patterns('inthe_am.taskmanager.views',
    url('^api/', include(api.urls)),
    url('^', 'home', name='home'),
)
