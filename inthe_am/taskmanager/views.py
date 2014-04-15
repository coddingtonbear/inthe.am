import datetime
import logging
import os
import re
import time

import pytz

from django.conf import settings
from django_sse.views import BaseSseView
from django.template.response import TemplateResponse

from .models import TaskStore, TaskStoreActivityLog


logger = logging.getLogger(__name__)


class Status(BaseSseView):
    UUID_MATCHER = re.compile(r'uuid:"([0-9a-zA-Z-]+)"')

    def get_store(self):
        if getattr(self, '_store', None) is None:
            if not self.request.user.is_authenticated():
                return None
            try:
                store = TaskStore.objects.get(user=self.request.user)
                setattr(self, '_store', store)
            except TaskStore.DoesNotExist:
                return None

        return self._store

    def get_changed_ids(self, store, head1, head2):
        proc = store._git_command(
            'diff', head1, head2
        )
        stdout, stderr = proc.communicate()

        changed_tickets = set()
        for raw_line in stdout.split('\n'):
            line = raw_line.strip()
            if not line or line[0] not in ('+', '-'):
                continue
            matched = self.UUID_MATCHER.search(line)
            if matched:
                changed_tickets.add(
                    matched.group(1)
                )

        return changed_tickets

    def check_head(self, head):
        store = self.get_store()
        new_head = store.repository.head()
        if head != new_head:
            logger.info('Found new repository head -- %s' % new_head)
            ids = self.get_changed_ids(store, head, new_head)
            for id in ids:
                self.sse.add_message("task_changed", id)
            head = new_head
            self.sse.add_message("head_changed", new_head)
        return head

    def get_taskd_mtime(self, store):
        try:
            taskd_mtime = os.path.getmtime(store.taskd_data_path)
        except OSError:
            taskd_mtime = 0
        return taskd_mtime

    def iterator(self):
        last_checked = datetime.datetime.now().replace(tzinfo=pytz.UTC)
        store = self.get_store()
        if not store:
            return
        store.sync(async=False)
        created = time.time()
        last_sync = time.time()
        taskd_mtime = self.get_taskd_mtime(store)
        head = self.request.GET.get('head', store.repository.head())
        while time.time() - created < settings.EVENT_STREAM_TIMEOUT:
            entries = TaskStoreActivityLog.objects.filter(
                last_seen__gt=last_checked,
                error=True,
                store=store,
            )
            last_checked = datetime.datetime.now().replace(tzinfo=pytz.UTC)
            for entry in entries:
                self.sse.add_message(
                    'error_logged',
                    entry.message
                )

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
                    store.sync(async=False)
                    head = self.check_head(head)
            else:
                if time.time() - last_sync > (
                    settings.EVENT_STREAM_POLLING_INTERVAL
                ):
                    last_sync = time.time()
                    store.sync(async=False)

                head = self.check_head(head)

            self.sse.add_message("heartbeat", str(time.time()))

            yield

            time.sleep(settings.EVENT_STREAM_LOOP_INTERVAL)


def home(request):
    try:
        store = TaskStore.objects.get(user=request.user)
        store.sync(async=False)
    except:
        pass
    return TemplateResponse(
        request,
        'home.html',
        {
            'DEBUG': settings.DEBUG,
        }
    )
