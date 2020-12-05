"""
WSGI config for Inthe.AM's status server.
"""

from collections import abc
import datetime
import json
import logging
import logging.config
import pickle
from queue import Queue
import time
import urllib.parse as urlparse
from typing import Optional, Union, Mapping, Set
from typing_extensions import TypedDict, Protocol

from dulwich.repo import Repo
from redis.client import PubSub
from wsgiref import util as wsgiref_utils

from inthe_am.taskmanager.types import announcements

import django

django.setup()

from django.conf import settings  # noqa: E402

from gevent import sleep  # noqa: E402

from inthe_am.taskmanager.lock import get_lock_redis  # noqa: E402


logger = logging.getLogger("inthe_am.wsgi_status")
logging.config.dictConfig(settings.LOGGING)


class SerializedTaskStore(Protocol):
    pk: str
    repository: Repo

    def sync(self, *args, **kwargs):
        ...

    def get_changed_task_ids(self, head: str) -> Set[str]:
        ...


class PubSubMessage(TypedDict):
    type: str
    pattern: Optional[bytes]
    channel: Optional[bytes]
    data: bytes


class QueuedMessage(TypedDict):
    name: str
    data: str


def get_announcements_subscription(store, username, channels) -> PubSub:
    client = get_lock_redis()
    subscription = client.pubsub(ignore_subscribe_messages=True)

    final_channels = []

    for channel in channels:
        final_channels.append(channel)

    subscription.subscribe(*channels)

    return subscription


def sse_offload(env, start_response):
    app = Application(env, start_response)

    for row in app.generator():
        yield row.encode("utf-8")


class Application:
    HEADERS = [
        ("Content-Type", "text/event-stream"),
    ]
    ERROR_RETRY_DELAY = 60 * 1000
    queue: "Queue[QueuedMessage]"
    head: str
    last_heartbeat: datetime.datetime
    initialized: bool
    store: SerializedTaskStore
    username: str

    def add_message(self, name: str, data: Optional[Union[str, Mapping]] = None):
        encoded = ""

        if data is None:
            pass
        elif isinstance(data, abc.Mapping):
            encoded = json.dumps(data)
        else:
            encoded = data

        logger.debug("Adding message %s: %s", name, encoded)

        self.queue.put({"name": name, "data": encoded})

    def handle_local_sync(self, message: PubSubMessage):
        local_sync: announcements.LocalSync = json.loads(message["data"])
        new_head: str = local_sync["head"]

        self.add_message("local_sync", local_sync)

        if new_head != self.head:
            self.head = new_head
            self.add_message("head_changed", self.head)

    def handle_changed_task(self, message: PubSubMessage):
        changed_task: announcements.ChangedTask = json.loads(message["data"])
        task_id = changed_task["task_id"]

        self.add_message("task_changed", task_id)

    def handle_log_message(self, message: PubSubMessage):
        log_msg: announcements.LogMessage = json.loads(message["data"])

        if log_msg["error"] and not log_msg["silent"]:
            self.add_message("error_logged", log_msg["message"])

    def handle_personal_announcement(self, message: PubSubMessage):
        announcement: announcements.PrivateAnnouncement = json.loads(message["data"])

        self.add_message("personal_announcement", announcement)

    def handle_message(self, message: PubSubMessage) -> bool:
        channel_info = message["channel"]
        if not channel_info:
            return False

        channel = channel_info.decode("utf-8")
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
        self.initialized = False
        self.queue = Queue()

        client = get_lock_redis()
        pickled_data = pickle.loads(client.get(f"pickle_{env['PICKLE_ID']}"))
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
                    f"local_sync.{self.username}",
                    f"changed_task.{self.username}",
                    f"log_message.{self.username}",
                    f"personal.{self.username}",
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
                yield f"retry: {self.ERROR_RETRY_DELAY}\n\n"
                return

            self.beat_heart()
            created = time.time()
            while time.time() - created < settings.EVENT_STREAM_TIMEOUT:
                self.beat_heart()

                # Queue-up all messages that have occurred
                while True:
                    message = self.subscription.get_message()
                    logger.debug("Found message: %s", message)
                    if not message:
                        break

                    self.handle_message(message)

                # Emit queued messages
                while not self.queue.empty():
                    message = self.queue.get(False)
                    if not message:
                        continue

                    logger.debug("Emitting %s on bus", message)
                    if message.get("name"):
                        yield f"event: {message['name']}\n"
                    yield f"data: {message.get('data', '')}\n"
                    yield "\n"

                # Relax
                sleep(settings.EVENT_STREAM_LOOP_INTERVAL)
            self.subscription.unsubscribe()
            self.subscription.close()
        except Exception:
            self.subscription.unsubscribe()
            self.subscription.close()
            raise


try:
    application = sse_offload
except Exception as e:
    logging.exception("Event stream terminated by uncaught exception: %s", str(e))
