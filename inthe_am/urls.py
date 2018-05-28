from django.contrib.auth import logout
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponseRedirect

from django.contrib import admin
admin.autodiscover()


def logout_and_redirect(request):
    logout(request)
    return HttpResponseRedirect('/')


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url('^logout/', logout_and_redirect, name='logout'),
    url('', include('social_django.urls', namespace='social')),
    url('', include('inthe_am.taskmanager.urls')),
) + staticfiles_urlpatterns()
