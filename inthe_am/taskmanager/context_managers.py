from contextlib import contextmanager
import datetime
import logging
import os

from django.conf import settings
from django.utils.timezone import now, utc

from lockfile import LockTimeout
from lockfile.pidlockfile import PIDLockFile


logger = logging.getLogger(__name__)


@contextmanager
def git_checkpoint(
    store, message, function=None, args=None, kwargs=None, sync=False
):
    pre_work_sha = store.repository.head()
    lockfile_path = os.path.join(store.local_path, '.lock')
    try:
        with PIDLockFile(lockfile_path, timeout=10):
            store.create_git_checkpoint(
                message,
                function=function,
                args=args,
                kwargs=kwargs,
                pre_operation=True
            )
            yield
            store.create_git_checkpoint(
                message,
                function=function,
                args=args,
                kwargs=kwargs
            )
    except LockTimeout:
        lockfile_created = datetime.datetime.fromtimestamp(
            os.path.getctime(lockfile_path)
        ).replace(tzinfo=utc)
        creation_minimum = (
            now() - datetime.timedelta(
                seconds=settings.LOCKFILE_TIMEOUT_SECONDS
            )
        )
        if lockfile_created < creation_minimum:
            store.log_error(
                "An expired lockfile was found and deleted. "
                "Although the request that caused the lockfile to be "
                "deleted did fail, subsequent requests will "
                "be successful."
            )
            os.unlink(lockfile_path)
        raise
    except Exception as e:
        store.create_git_checkpoint(
            str(e),
            function=function,
            args=args,
            kwargs=kwargs,
            rollback=True
        )
        dangling_sha = store.repository.head()
        if dangling_sha != pre_work_sha:
            logger.exception(
                "An error occurred that required rolling-back "
                "the git repository at %s from %s to %s.",
                store.local_path,
                dangling_sha,
                pre_work_sha,
            )
            store.log_error(
                "An error occurred while interacting with your task list, "
                "and your task list was recovered by rolling-back to the "
                "last known good state (%s).  Since your task list is "
                "synchronized with a taskd server, this will likely not "
                "have any negative effects.  Rollback ID: %s.",
                pre_work_sha,
                dangling_sha,
            )
            store.git_reset(pre_work_sha)
        raise
    if sync:
        store.sync()
