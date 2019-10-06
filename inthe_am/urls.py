from django.contrib import admin
from django.contrib.auth import logout
from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from inthe_am.taskmanager.models import TaskStore

admin.autodiscover()

try:
    import uwsgi
except ImportError:
    uwsgi = None


def logout_and_redirect(request):
    logout(request)
    return HttpResponseRedirect('/')


def status_offload(request):
    if not uwsgi:
        return JsonResponse(
            {
                'error': 'Status unavailable in this environment.',
            },
            status_code=404,
        )

    if not request.user.is_authenticated():
        return JsonResponse(
            {
                'error': 'Unauthenticated',
            },
            status_code=401
        )

    taskstore = TaskStore.get_for_user(request.user)

    uwsgi.route("TASKSTORE_ID", taskstore.pk)
    uwsgi.route("uwsgi", "/tmp/inthe_am_status.sock,0,0")
    return HttpResponse()


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/', logout_and_redirect, name='logout'),
    url(r'^status/', status_offload),
    url('', include('social_django.urls', namespace='social')),
    url('', include('inthe_am.taskmanager.urls')),
 ] + staticfiles_urlpatterns()
