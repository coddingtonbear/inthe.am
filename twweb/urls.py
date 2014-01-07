import json

from django.contrib.auth import logout
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponseRedirect, HttpResponse

from django.contrib import admin
admin.autodiscover()

def is_secure(request):
    return HttpResponse(
        json.dumps(
            {
                'is_secure': request.is_secure(),
                'meta': request.META,
            }
        ),
        content_type='application/x-json'
    )


def logout_and_redirect(request):
    logout(request)
    return HttpResponseRedirect('/')


urlpatterns = patterns('',
    url(r'^is_secure/', is_secure),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^accounts/', include('django.contrib.auth.urls')),
    url('^logout/', logout_and_redirect, name='logout'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('twweb.taskmanager.urls')),
) + staticfiles_urlpatterns()
