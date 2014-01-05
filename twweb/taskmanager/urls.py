from tastypie.api import Api

from django.conf.urls import include, patterns, url

from .api import UserResource

api = Api(api_name='v1')
api.register(UserResource())


urlpatterns = patterns('twweb.taskmanager.views',
    url('^api/', include(api.urls)),
    url('^$', 'home', name='home'),
)
