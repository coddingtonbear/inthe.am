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
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB
    )


def get_debounce_name_for_store(store):
    return store.user.username + '.sync.debounce'


def get_lock_name_for_store(store):
    return store.user.username + ".lock"


@contextmanager
def redis_lock(
    name,
    wait_timeout=settings.LOCKFILE_WAIT_TIMEOUT,
    lock_timeout=settings.LOCKFILE_TIMEOUT_SECONDS,
    lock_check_interval=settings.LOCKFILE_CHECK_INTERVAL,
    message=''
):
    client = get_lock_redis()
    started = time.time()
    wait_expiry = time.time() + wait_timeout

    while(time.time() < wait_expiry):
        lock_expiry = time.time() + lock_timeout + 1
        result = client.setnx(name, str(lock_expiry))
        if result:
            logger.debug(
                "Acquired lock %s; took %s seconds",
                name,
                time.time() - started
            )
            # Got the lock!
            yield
            # Make sure that this operation didn't take longer than
            # a lock timeout -- if it did, don't delete the key, it might
            # be somebody elses!
            if lock_expiry > time.time():
                client.delete(name)
                logger.debug(
                    "Lock %s released",
                    name,
                )
            else:
                logger.warning(
                    "Lock %s expired before operation completed "
                    "(%s seconds ago)",
                    name,
                    time.time() - lock_expiry
                )
            return

        # Didn't get the lock!
        original_timestamp = client.get(name)
        if float(original_timestamp) > time.time():
            # The timestamp isn't yet expired, let's wait a second
            # and try again.
            time.sleep(lock_check_interval)
            continue
        else:
            logger.debug(
                "Lock %s expired %s seconds ago; attempting to steal lock.",
                name,
                time.time() - float(original_timestamp)
            )

        getset_timestamp = client.getset(name, str(lock_expiry))
        if getset_timestamp == original_timestamp:
            logger.debug(
                "Lock %s successfully stolen.",
                name,
            )
            yield
            # Make sure that this operation didn't take longer than
            # a lock timeout -- if it did, don't delete the key, it might
            # be somebody elses!
            if lock_expiry > time.time():
                client.delete(name)
                logger.debug(
                    "Lock %s (stolen) released",
                    name,
                )
            else:
                logger.warning(
                    "Lock %s (stolen) expired before operation completed "
                    "(%s seconds ago)",
                    name,
                    time.time() - lock_expiry
                )
            return
        else:
            # Somebody else got it first, let's wait a second
            # and try again.
            logger.debug(
                "Lock %s was not successfully stolen.",
                name,
            )
            time.sleep(lock_check_interval)
            continue

    logger.warning(
        "Unable to acquire lock %s '%s' (waited %s seconds); "
        "raising LockTimeout",
        name,
        message,
        time.time() - started,
        extra={
            'stack': True,
        }
    )
    raise LockTimeout("Unable to acquire lock %s" % name)
