"""
WSGI config for Inthe.AM's status server.
"""

import datetime
import json
import logging
import os
import pickle
from queue import Queue
import time
import urllib.parse as urlparse
from wsgiref import util as wsgiref_utils

import django

django.setup()  # noqa

from django.conf import settings
from django.core.signing import Signer

from gevent import sleep

from inthe_am.taskmanager.lock import get_lock_redis

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inthe_am.settings")

logger = logging.getLogger("inthe_am.wsgi_status")
logging.config.dictConfig(settings.LOGGING)


def get_announcements_subscription(store, username, channels):
    client = get_lock_redis()
    subscription = client.pubsub(ignore_subscribe_messages=True)

    final_channels = []

    for channel in channels:
        final_channels.append(channel.format(username=username.encode("utf8")))

    subscription.subscribe(*channels)

    return subscription


def sse_offload(env, start_response):
    app = Application(env, start_response)

    for row in app.generator():
        yield row.encode("utf-8")


class Application(object):
    HEADERS = [
        ("Content-Type", "text/event-stream"),
    ]
    ERROR_RETRY_DELAY = 60 * 1000

    def add_message(self, name, data=None):
        if data is None:
            data = ""

        self.queue.put(
            {"name": name, "data": data,}
        )

    def handle_local_sync(self, message):
        new_head = json.loads(message["data"])["head"]

        self.add_message("local_sync", message["data"])

        if new_head != self.head:
            self.head = new_head
            self.add_message("head_changed", self.head)

    def handle_changed_task(self, message):
        self.add_message("task_changed", json.loads(message["data"])["task_id"])

    def handle_log_message(self, message):
        announcement = json.loads(message["data"])
        if announcement["error"] and not announcement["silent"]:
            self.add_message("error_logged", announcement["message"])

    def handle_personal_announcement(self, message):
        self.add_message("personal_announcement", message["data"])

    def handle_public_announcement(self, message):
        message_data = json.loads(message["data"])

        # Open the envelope, see if it's a system announcement or not.
        if not message_data.get("system", False):
            self.add_message("public_announcement", message["data"])
        else:
            self.add_message(message_data["type"], json.dumps(message_data["data"]))

    def handle_message(self, message):
        channel = message["channel"].decode("utf-8")
        if channel.startswith("local_sync."):
            self.handle_local_sync(message)
            return True
        elif channel.startswith("changed_task."):
            self.handle_changed_task(message)
            return True
        elif channel.startswith("log_message."):
            self.handle_log_message(message)
            return True
        elif channel.startswith("personal."):
            self.handle_personal_announcement(message)
            return True
        elif channel == settings.ANNOUNCEMENTS_CHANNEL:
            return True

        return False

    def beat_heart(self):
        heartbeat_interval = datetime.timedelta(
            seconds=settings.EVENT_STREAM_HEARTBEAT_INTERVAL
        )
        if (
            not self.last_heartbeat
            or self.last_heartbeat + heartbeat_interval < datetime.datetime.now()
        ):
            self.add_message("heartbeat")
            self.last_heartbeat = datetime.datetime.now()

    def __init__(self, env, start_response):
        start_response("200 OK", self.HEADERS)

        self.last_heartbeat = None
        self.env = env
        self.response = env
        self.signer = Signer()
        self.initialized = False
        self.queue = Queue()

        client = get_lock_redis()
        pickled_data = pickle.loads(client.get("pickle_{}".format(env["PICKLE_ID"])))
        self.store = pickled_data["taskstore"]
        self.username = pickled_data["username"]

        try:
            logger.info(
                "Starting event stream for TaskStore %s for user %s",
                self.store.pk,
                self.username,
            )
            query = urlparse.parse_qs(
                urlparse.urlparse(wsgiref_utils.request_uri(env)).query
            )
            try:
                self.head = query["head"][0]
            except (KeyError, IndexError):
                self.head = self.store.repository.head().decode("utf-8")

            # Subscribe to the event stream
            self.subscription = get_announcements_subscription(
                self.store,
                self.username,
                [
                    "local_sync.{username}",
                    "changed_task.{username}",
                    "log_message.{username}",
                    "personal.{username}",
                    settings.ANNOUNCEMENTS_CHANNEL,
                ],
            )

            # Kick-off a sync just to be sure
            kwargs = {"asynchronous": True, "function": ("views.Status.iterator")}
            self.store.sync(msg="Iterator initialization", **kwargs)

            # Let the client know the head has changed if they've asked
            # for a different head than the one we're on:
            if self.head != self.store.repository.head().decode("utf-8"):
                for task_id in self.store.get_changed_task_ids(self.head):
                    self.add_message("task_changed", task_id)

            self.initialized = True

        except Exception as e:
            logger.exception("Error starting event stream: %s", str(e))

    def generator(self):
        try:
            if not self.initialized:
                yield "retry: %s\n\n" % self.ERROR_RETRY_DELAY
                return

            self.beat_heart()
            created = time.time()
            while time.time() - created < settings.EVENT_STREAM_TIMEOUT:
                self.beat_heart()

                # Queue-up all messages that have occurred
                while True:
                    message = self.subscription.get_message()
                    if not message:
                        break

                    self.handle_message(message)

                # Emit queued messages
                while not self.queue.empty():
                    message = self.queue.get(False)
                    if not message:
                        continue

                    if message.get("name"):
                        yield "event: {name}\n".format(name=message["name"])
                    yield "data: {data}\n".format(data=message.get("data", ""))
                    yield "\n"

                # Relax
                sleep(settings.EVENT_STREAM_LOOP_INTERVAL)
            self.subscription.unsubscribe()
            self.subscription.close()
        except Exception as e:
            self.subscription.unsubscribe()
            self.subscription.close()
            raise


try:
    application = sse_offload
except Exception as e:
    logging.exception("Event stream terminated by uncaught exception: %s", str(e))
