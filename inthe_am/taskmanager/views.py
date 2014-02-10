import logging
import re
import time

from django_sse.views import BaseSseView
from django.template.response import TemplateResponse

from .models import TaskStore


logger = logging.getLogger(__name__)


class Status(BaseSseView):
    UUID_MATCHER = re.compile(r'uuid:"([0-9a-zA-Z-]+)"')

    def get_store(self):
        if getattr(self, '_store', None) is None:
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

    def iterator(self):
        store = self.get_store()
        store.sync()
        created = time.time()
        last_sync = time.time()
        head = self.request.GET.get('head', store.repository.head())
        while time.time() - created < 240:
            if time.time() - last_sync > 15:
                last_sync = time.time()
                store.sync()

            store = self.get_store()
            new_head = store.repository.head()
            if head != new_head:
                logger.info('Found new repository head -- %s' % new_head)
                ids = self.get_changed_ids(store, head, new_head)
                for id in ids:
                    self.sse.add_message("task_changed", id)
                head = new_head
                self.sse.add_message("head_changed", new_head)
            else:
                self.sse.add_message("heartbeat", str(time.time()))

            yield
            time.sleep(5)


def home(request):
    return TemplateResponse(
        request,
        'home.html',
        {}
    )
