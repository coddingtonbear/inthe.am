import datetime
import json
import logging
import time

from django_sse.views import BaseSseView
import pytz

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect

from .models import KanbanBoard, TaskStore, TaskStoreActivityLog
from .lock import (
    get_announcements_subscription,
    get_lock_name_for_store,
    redis_lock,
    LockTimeout
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

    def beat_heart(self):
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
                        'sync_enabled': True,  # This might be a lie!
                    }
                )
            )
            self._last_heartbeat = datetime.datetime.now()

    def process_messages(self, subscription):
        envelope = subscription.get_message()
        while envelope:
            if envelope['type'] != 'message':
                continue
            try:
                data = json.loads(envelope['data'])
            except:
                logger.exception(
                    "Error decoding envelope data: %s",
                    envelope['data'],
                )
                continue

            if envelope['channel'].startswith('head_changed:'):
                self.sse.add_message(
                    "head_changed",
                    data['new_head'],
                )
            elif envelope['channel'].startswith('task_changed:'):
                self.sse.add_message(
                    "task_changed",
                    data['uuid'],
                )
            elif envelope['channel'].startswith('log:error:'):
                self.sse.add_message(
                    "error_logged",
                    data["message"],
                )

            # No message types are currently handled.
            envelope = subscription.get_message()

    def iterator(self):
        store = self.get_store()
        if not store:
            return

        subscription = get_announcements_subscription(
            store,
            announcement_types=[
                'head_changed',
                'task_changed',
                'log:error',
            ]
        )
        created = time.time()

        # Make sure that we are all in agreement about what the
        # head should be:
        repo_head = store.repository.head()
        requested_head = self.request.GET.get('head', repo_head)
        if requested_head != repo_head:
            self.sse.add_message(
                'head_changed',
                repo_head,
            )

        # Periodically retrieve new messages from pubsub, and return
        # those messages via SSE.
        self.beat_heart()
        while time.time() - created < settings.EVENT_STREAM_TIMEOUT:
            self.process_messages(subscription)

            store = self.get_store(cached=False)

            self.beat_heart()

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
