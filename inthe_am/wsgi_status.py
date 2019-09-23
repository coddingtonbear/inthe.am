"""
WSGI config for Inthe.AM's status server.
"""
import datetime
import json
import logging
import os
from queue import Queue
import time
import urllib.parse as urlparse
from wsgiref import util as wsgiref_utils

import django
django.setup()  # noqa

from django.conf import settings
from django.core.signing import Signer
from gevent import sleep
from psycogreen.gevent import patch_psycopg

from inthe_am.taskmanager.models import TaskStore
from inthe_am.taskmanager.lock import get_announcements_subscription


patch_psycopg()


logger = logging.getLogger(__name__)
logging.config.dictConfig(settings.LOGGING)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inthe_am.settings")


class Application(object):
    HEADERS = [
        ('Content-Type', 'text/event-stream'),
    ]
    ERROR_RETRY_DELAY = 60 * 1000

    def add_message(self, name, data=None):
        if data is None:
            data = ''

        self.queue.put(
            {
                'name': name,
                'data': data,
            }
        )

    def handle_local_sync(self, message):
        new_head = json.loads(message['data'])['head']

        self.add_message('local_sync', message['data'])

        if new_head != self.head:
            self.head = new_head
            self.add_message('head_changed', self.head)

    def handle_changed_task(self, message):
        self.add_message(
            'task_changed',
            json.loads(message['data'])['task_id']
        )

    def handle_log_message(self, message):
        announcement = json.loads(message['data'])
        if announcement['error'] and not announcement['silent']:
            self.add_message(
                'error_logged',
                announcement['message']
            )

    def handle_personal_announcement(self, message):
        self.add_message('personal_announcement', message['data'])

    def handle_public_announcement(self, message):
        message_data = json.loads(message['data'])

        # Open the envelope, see if it's a system announcement or not.
        if not message_data.get('system', False):
            self.add_message('public_announcement', message['data'])
        else:
            self.add_message(
                message_data['type'],
                json.dumps(message_data['data'])
            )

    def beat_heart(self):
        heartbeat_interval = datetime.timedelta(
            seconds=settings.EVENT_STREAM_HEARTBEAT_INTERVAL
        )
        if (
            not self.last_heartbeat or
            self.last_heartbeat + heartbeat_interval < datetime.datetime.now()
        ):
            self.add_message("heartbeat")
            self.last_heartbeat = datetime.datetime.now()

    def __init__(self, env, start_response):
        start_response('200 OK', self.HEADERS)
        self.last_heartbeat = None
        self.env = env
        self.response = env
        self.signer = Signer()
        self.initialized = False
        self.queue = Queue()

        try:
            query = urlparse.parse_qs(
                urlparse.urlparse(
                    wsgiref_utils.request_uri(env)
                ).query
            )
            if 'key' not in query:
                return
            taskstore_id = self.signer.unsign(query['key'][0])
            self.store = TaskStore.objects.get(pk=int(taskstore_id))
            try:
                self.head = query['head'][0]
            except (KeyError, IndexError):
                self.head = self.store.repository.head().decode('utf-8')

            # Subscribe to the event stream
            self.subscription = get_announcements_subscription(
                self.store,
                **{
                    'local_sync.{username}': self.handle_local_sync,
                    'changed_task.{username}': self.handle_changed_task,
                    'log_message.{username}': self.handle_log_message,
                    'personal.{username}': self.handle_personal_announcement,
                    settings.ANNOUNCEMENTS_CHANNEL: (
                        self.handle_public_announcement
                    ),
                }
            )
            self.subscription_thread = self.subscription.run_in_thread(
                sleep_time=1
            )

            # Kick-off a sync just to be sure
            kwargs = {
                'async': True,
                'function': (
                    'views.Status.iterator'
                )
            }
            self.store.sync(msg='Iterator initialization', **kwargs)

            # Let the client know the head has changed if they've asked
            # for a different head than the one we're on:
            if self.head != self.store.repository.head().decode('utf-8'):
                for task_id in self.store.get_changed_task_ids(self.head):
                    self.add_message('task_changed', task_id)

            self.initialized = True
        except Exception as e:
            logger.exception("Error starting event stream: %s", str(e))

    def __iter__(self):
        try:
            if not self.initialized:
                yield 'retry: %s\n\n' % self.ERROR_RETRY_DELAY
                return

            self.beat_heart()
            created = time.time()
            while time.time() - created < settings.EVENT_STREAM_TIMEOUT:
                self.beat_heart()

                # Emit queued messages
                while not self.queue.empty():
                    message = self.queue.get(False)
                    if not message:
                        continue

                    if message.get('name'):
                        yield 'event: {name}\n'.format(
                            name=message['name'].encode('utf8')
                        )
                    yield 'data: {data}\n'.format(
                        data=message.get('data', '').encode('utf8')
                    )
                    yield '\n'

                # Relax
                sleep(settings.EVENT_STREAM_LOOP_INTERVAL)
            self.subscription_thread.stop()
            self.subscription.close()
        except:
            self.subscription_thread.stop()
            self.subscription.close()
            raise

try:
    application = Application
except Exception as e:
    logging.exception(
        'Event stream terminated by uncaught exception: %s',
        str(e)
    )
