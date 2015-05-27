import datetime
import json
import logging
import time

from django_sse.views import BaseSseView

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect

from .models import KanbanBoard, TaskStore
from .lock import (
    get_announcements_subscription,
)


logger = logging.getLogger(__name__)


class Status(BaseSseView):
    def get_store(self, cached=True):
        if not cached or getattr(self, '_store', None) is None:
            if not self.request.user.is_authenticated():
                return None

            if 'uuid' in self.kwargs:
                store = KanbanBoard.objects.get(uuid=self.kwargs['uuid'])
                if not store.user_is_member(self.request.user):
                    return None
                setattr(self, '_store', store)
            else:
                try:
                    store = TaskStore.objects.get(user=self.request.user)
                    setattr(self, '_store', store)
                except TaskStore.DoesNotExist:
                    return None

        return self._store

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

    def handle_local_sync(self, message):
        self.sse.add_message(
            'head_changed',
            json.loads(message['data'])['head']
        )

    def handle_changed_task(self, message):
        self.sse.add_message(
            'task_changed',
            json.loads(message['data'])['task_id']
        )

    def handle_log_message(self, message):
        self.sse.add_message(
            'error_logged',
            json.loads(message['data'])['message']
        )

    def handle_personal_announcement(self, message):
        self.sse.add_message(
            'personal_announcement',
            json.loads(message['data'])['message']
        )

    def handle_public_announcement(self, message):
        self.sse.add_message(
            'public_announcement',
            json.loads(message['data'])['message']
        )

    def iterator(self):
        store = self.get_store()
        if not store:
            return

        subscription = get_announcements_subscription(
            store,
            **{
                'local_sync.{username}': self.handle_local_sync,
                'changed_task.{username}': self.handle_changed_task,
                'log_message.{username}': self.handle_log_message,
                '{username}': self.handle_personal_announcement,
                settings.ANNOUNCEMENTS_CHANNEL: (
                    self.handle_public_announcement
                ),
            }
        )
        subscription_thread = subscription.run_in_thread(sleep_time=0.01)

        # Kick-off a sync just to be sure
        kwargs = {
            'async': True,
            'function': (
                'views.Status.iterator'
            )
        }
        store.sync(msg='Iterator initialization', **kwargs)

        # If our head doesn't match the current repository head,
        # let the client know what has changed.
        head = self.request.GET.get('head', store.repository.head())
        if head != store.repository.head():
            for task_id in store.get_changed_task_ids(head):
                self.sse.add_message(
                    'task_changed',
                    task_id,
                )

        self.beat_heart(store)
        created = time.time()
        while time.time() - created < settings.EVENT_STREAM_TIMEOUT:
            # Heartbeat
            store = self.get_store(cached=False)
            self.beat_heart(store)

            # Emit queued messages
            yield

            # Relax
            time.sleep(settings.EVENT_STREAM_LOOP_INTERVAL)

        subscription_thread.stop()


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
            lines.append(u'{k}: {v}'.format(k=k, v=v))
        return '\n'.join(lines)

    def item_link(self, item):
        return u'/tasks/{uuid}'.format(uuid=item.get('uuid'))

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
            u"Highest urgency tasks on {first_name} {last_name}'s "
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
        return u"{first_name} {last_name}'s tasks".format(
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
