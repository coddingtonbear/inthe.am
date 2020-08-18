from contextlib import contextmanager
import logging
import time

import redis

from django.conf import settings


logger = logging.getLogger(__name__)


class LockTimeout(Exception):
    pass


def get_lock_redis():
    return redis.StrictRedis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
    )


def get_announcements_subscription(store, **kwargs):
    client = get_lock_redis()
    subscription = client.pubsub(ignore_subscribe_messages=True)

    final_channels = {}

    for announcement_type, handler in kwargs.items():
        name = announcement_type.format(username=store.username.encode("utf8"))
        final_channels[name] = handler

    subscription.subscribe(**final_channels)

    return subscription


def get_debounce_name_for_store(store, subtype=None):
    return ".".join([store.username, subtype if subtype else "sync", "debounce",])


def get_lock_name_for_store(store):
    return store.username + ".lock"


@contextmanager
def redis_lock(
    name,
    wait_timeout=settings.LOCKFILE_WAIT_TIMEOUT,
    lock_timeout=settings.LOCKFILE_TIMEOUT_SECONDS,
    lock_check_interval=settings.LOCKFILE_CHECK_INTERVAL,
    message="",
):
    client = get_lock_redis()
    started = time.time()
    wait_expiry = time.time() + wait_timeout

    while time.time() < wait_expiry:
        lock_expiry = time.time() + lock_timeout + 1
        result = client.setnx(name, str(lock_expiry))
        if result:
            logger.debug(
                "Acquired lock %s; took %s seconds", name, time.time() - started
            )
            # Got the lock!
            try:
                yield
            except:
                client.delete(name)
                raise
            # Make sure that this operation didn't take longer than
            # a lock timeout -- if it did, don't delete the key, it might
            # be somebody elses!
            if lock_expiry > time.time():
                client.delete(name)
                logger.debug(
                    "Lock %s released", name,
                )
            else:
                logger.warning(
                    "Lock %s expired before operation completed " "(%s seconds ago)",
                    name,
                    time.time() - lock_expiry,
                )
            return

        # Didn't get the lock!
        original_timestamp = client.get(name)
        if original_timestamp and float(original_timestamp) > time.time():
            # The timestamp isn't yet expired, let's wait a second
            # and try again.
            time.sleep(lock_check_interval)
            continue
        else:
            logger.debug("Lock %s expired; attempting to steal lock.", name)

        getset_timestamp = client.getset(name, str(lock_expiry))
        if getset_timestamp == original_timestamp:
            logger.debug(
                "Lock %s successfully stolen.", name,
            )
            try:
                yield
            except:
                client.delete(name)
                raise
            # Make sure that this operation didn't take longer than
            # a lock timeout -- if it did, don't delete the key, it might
            # be somebody elses!
            if lock_expiry > time.time():
                client.delete(name)
                logger.debug(
                    "Lock %s (stolen) released", name,
                )
            else:
                logger.warning(
                    "Lock %s (stolen) expired before operation completed "
                    "(%s seconds ago)",
                    name,
                    time.time() - lock_expiry,
                )
            return
        else:
            # Somebody else got it first, let's wait a second
            # and try again.
            logger.debug(
                "Lock %s was not successfully stolen.", name,
            )
            time.sleep(lock_check_interval)
            continue

    logger.warning(
        "Unable to acquire lock %s '%s' (waited %s seconds); " "raising LockTimeout",
        name,
        message,
        time.time() - started,
        extra={"stack": True,},
        exc_info=True,
    )
    raise LockTimeout("Unable to acquire lock %s" % name)
