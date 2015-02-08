import json
import logging
import redis
import socket
import time

from django.core.management.base import BaseCommand

from inthe_am.taskmanager.lock import get_lock_redis
from inthe_am.taskmanager.models import KanbanBoard, TaskStore


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def get_redis_connection(self):
        if not hasattr(self, '_redis'):
            self._redis = get_lock_redis()
            self._subscription = None
        try:
            self._redis.ping()
        except redis.ConnectionError:
            self._redis = get_lock_redis()
            self._subscription = None

        return self._redis

    def get_subscription(self):
        connection = self.get_redis_connection()

        if not self._subscription:
            self._subscription = connection.pubsub()
            self._subscrption.psubscribe('sync.*')

        return self._subscription

    def get_next_message(self):
        subscription = self.get_subscription()
        return subscription.get_message()

    def operation_requires_sync(self, op):
        if (
            (
                op['stored_count'] > 0 or op['merged_count'] > 0
            )
            and (
                op['ip'] not in self.local_ips
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
        while True:
            message = self.get_next_message()

            if not message:
                time.sleep(0.1)
                continue

            try:
                operation = json.loads(message['data'])
                if self.operation_requires_sync(operation):
                    repo = self.get_taskstore_for_operation(operation)
                    logger.debug(
                        "Queueing sync for %s",
                        repo,
                    )
                    repo.sync()
            except:
                logger.exception(
                    "Error encountered while processing sync event."
                )
