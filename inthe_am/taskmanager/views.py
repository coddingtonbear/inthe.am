import datetime
import json
import logging
import os
import time

from django_sse.views import BaseSseView
import pytz

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect

from .models import TaskStore, TaskStoreActivityLog
from .lock import get_lock_name_for_store, redis_lock, LockTimeout


logger = logging.getLogger(__name__)


class Status(BaseSseView):
    def get_store(self, cached=True):
        if not cached or getattr(self, '_store', None) is None:
            if not self.request.user.is_authenticated():
                return None
            try:
                store = TaskStore.objects.get(user=self.request.user)
                setattr(self, '_store', store)
            except TaskStore.DoesNotExist:
                return None

        return self._store

    def check_head(self, head):
        store = self.get_store()
        new_head = store.repository.head()

        try:
            if head != new_head:
                with redis_lock(
                    get_lock_name_for_store(store),
                    message="SSE Head Change"
                ):
                    logger.info('Found new repository head -- %s' % new_head)
                    ids = store.get_changed_task_ids(head, new_head)
                    for id in ids:
                        self.sse.add_message("task_changed", id)
                    head = new_head
                    self.sse.add_message("head_changed", new_head)
        except LockTimeout:
            # This is OK -- we'll check again on the next round.
            pass

        return head

    def get_taskd_mtime(self, store):
        try:
            taskd_mtime = os.path.getmtime(store.taskd_data_path)
        except OSError:
            taskd_mtime = 0
        return taskd_mtime

    def beat_heart(self, store):
        heartbeat_interval = datetime.timedelta(
            seconds=settings.EVENT_STREAM_HEARTBEAT_INTERVAL
        )
        last_heartbeat = getattr(
            self,
            '_last_heartbeat',
            datetime.datetime.now() - heartbeat_interval
        )
        if last_heartbeat + heartbeat_interval < datetime.datetime.now():
            self.sse.add_message(
                "heartbeat",
                json.dumps(
                    {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'sync_enabled': store.sync_enabled,
                    }
                )
            )
            self._last_heartbeat = datetime.datetime.now()

    def iterator(self):
        last_checked = datetime.datetime.now().replace(tzinfo=pytz.UTC)
        store = self.get_store()
        if not store:
            return
        kwargs = {
            'async': True,
            'function': (
                'views.Status.iterator'
            )
        }
        store.sync(msg='Iterator initialization', **kwargs)
        created = time.time()
        last_sync = time.time()
        taskd_mtime = self.get_taskd_mtime(store)
        head = self.request.GET.get('head', store.repository.head())
        self.beat_heart(store)
        while time.time() - created < settings.EVENT_STREAM_TIMEOUT:
            # Get Error/Log Messages
            entries = TaskStoreActivityLog.objects.filter(
                last_seen__gt=last_checked,
                error=True,
                silent=False,
                store=store,
            )
            for entry in entries:
                self.sse.add_message(
                    'error_logged',
                    entry.message
                )
            last_checked = datetime.datetime.now().replace(tzinfo=pytz.UTC)

            # See if our head has changed, and queue messages if so
            head = self.check_head(head)

            if store.using_local_taskd:
                new_mtime = self.get_taskd_mtime(store)
                if (
                    new_mtime != taskd_mtime
                    or (
                        (time.time() - last_sync)
                        > settings.EVENT_STREAM_POLLING_INTERVAL
                    )
                ):
                    taskd_mtime = new_mtime
                    last_sync = time.time()
                    store.sync(msg='Local mtime sync', **kwargs)
            else:
                if time.time() - last_sync > (
                    settings.EVENT_STREAM_POLLING_INTERVAL
                ):
                    last_sync = time.time()
                    store.sync(msg='Remote polling sync', **kwargs)

            store = self.get_store(cached=False)

            self.beat_heart(store)

            yield

            time.sleep(settings.EVENT_STREAM_LOOP_INTERVAL)


class TaskFeed(Feed):
    def get_object(self, request, uuid):
        try:
            store = TaskStore.objects.get(
                secret_id=uuid
            )
        except TaskStore.NotFound:
            raise Http404()

        if not store.feed_enabled:
            raise Http404()

        return store

    def item_title(self, item):
        return item.get('description')

    def item_description(self, item):
        lines = []
        for k, v in item.items():
            lines.append('{k}: {v}'.format(k=k, v=v))
        return '\n'.join(lines)

    def item_link(self, item):
        return '/tasks/{uuid}'.format(uuid=item.get('uuid'))

    def items(self, store):
        tasks = store.client.filter_tasks({'status': 'pending'})[0:100]
        tasks = sorted(
            tasks,
            key=lambda d: float(d['urgency']),
            reverse=True
        )
        return tasks

    def description(self, store):
        return (
            "Highest urgency tasks on {first_name} {last_name}'s "
            "task list.".format(
                first_name=store.user.first_name,
                last_name=store.user.last_name
            )
        )

    def link(self, store):
        return reverse(
            'feed', kwargs={'uuid': store.secret_id}
        )

    def title(self, store):
        return "{first_name} {last_name}'s tasks".format(
            first_name=store.user.first_name,
            last_name=store.user.last_name
        )


def debug_login(request):
    from inthe_am.taskmanager.debug_utils import artificial_login

    if not settings.DEBUG:
        raise SuspiciousOperation(
            "Artificial login attempted while not in debug mode!"
        )

    try:
        cookies = artificial_login(
            username=request.GET['username'],
            password=request.GET['password'],
        )
    except AttributeError:
        return HttpResponseBadRequest()
    response = HttpResponseRedirect('/')
    for name, value in cookies.items():
        response.set_cookie(name, value)
    return response
