import pickle
import uuid

from django.contrib import admin
from django.contrib.auth import logout
from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from inthe_am.taskmanager.lock import get_lock_redis
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
            status=404,
        )

    if not request.user.is_authenticated():
        return JsonResponse(
            {
                'error': 'Unauthenticated',
            },
            status=401
        )

    redis = get_lock_redis()

    taskstore = TaskStore.get_for_user(request.user)

    pickle_id = str(uuid.uuid4())
    pickled_taskstore = pickle.dumps(taskstore)

    redis.set(
        'taskstore_pickle_{}'.format(pickle_id),
        pickled_taskstore,
        ex=60
    )

    uwsgi.add_var("TASKSTORE_PICKLE_ID", str(pickle_id))
    uwsgi.add_var("USERNAME", request.user.username)
    uwsgi.add_var("OFFLOAD_TO_SSE", "y")
    uwsgi.add_var("OFFLOAD_SERVER", "/tmp/inthe_am_status.sock")
    return HttpResponse()


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/', logout_and_redirect, name='logout'),
    url(r'^status/', status_offload),
    url('', include('social_django.urls', namespace='social')),
    url('', include('inthe_am.taskmanager.urls')),
 ] + staticfiles_urlpatterns()
