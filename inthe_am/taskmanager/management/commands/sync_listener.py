import datetime
import json
import logging
import socket
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from inthe_am.taskmanager.lock import get_lock_redis
from inthe_am.taskmanager.models import KanbanBoard, TaskStore


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def get_redis_connection(self):
        if not hasattr(self, '_redis'):
            self._redis = get_lock_redis()
            self._subscription = None

        return self._redis

    def get_subscription(self):
        connection = self.get_redis_connection()

        if not self._subscription:
            self._subscription = connection.pubsub()
            self._subscription.psubscribe('sync.*')

        return self._subscription

    def get_next_message(self):
        subscription = self.get_subscription()
        return subscription.get_message()

    def operation_requires_sync(self, op):
        if (
            (
                op.get('stored_count', 0) > 0 or op.get('merged_count', 0) > 0
            )
            and (
                op.get('ip', '') not in self.local_ips
            )
        ):
            return True
        return False

    def get_taskstore_for_operation(self, op):
        group, username = op['username'].split('/')
        if username.startswith('taskstore'):
            return KanbanBoard.objects.get(
                pk=int(username[9:])
            )
        else:
            return TaskStore.objects.get(
                user__username=username
            )

    @property
    def local_ips(self):
        if not hasattr(self, '_local_ips'):
            self._local_ips = [
                socket.gethostbyname(socket.gethostname()),
                '127.0.0.1',
            ]
        return self._local_ips

    def handle(self, *args, **kwargs):
        self.last_sync_queued = None
        while True:
            message = self.get_next_message()

            if not message:
                time.sleep(0.1)
                continue
            if message['type'] != 'pmessage':
                continue

            try:
                operation = json.loads(message['data'])
                if self.operation_requires_sync(operation):
                    repo = self.get_taskstore_for_operation(operation)
                    logger.info(
                        "Queueing sync for %s",
                        repo,
                    )
                    repo.sync()
                    self.last_sync_queued = now()
            except:
                logger.exception(
                    "Error encountered while processing sync event."
                )

            if (
                self.last_sync_queued and
                (
                    (now() - self.last_sync_queued) >
                    datetime.timedelta(
                        seconds=settings.SYNC_LISTENER_WARNING_TIMEOUT
                    )
                )
            ):
                logger.warning(
                    "No synchronizations have been queued during the last %s "
                    "minutes;  it is likely that something is misconfigured.",
                    round((now() - self.last_sync_queued).seconds / 60.0)
                )
