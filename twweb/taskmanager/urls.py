from django.conf.urls import patterns, url

urlpatterns = patterns('twweb.taskmanager.views',
    url('^$', 'home', name='home'),
)
