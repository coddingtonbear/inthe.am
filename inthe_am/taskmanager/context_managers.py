from contextlib import contextmanager
import datetime
import os

from django.conf import settings
from django.utils.timezone import now, utc

from lockfile import LockTimeout
from lockfile.pidlockfile import PIDLockFile


@contextmanager
def git_checkpoint(
    store, message, function=None, args=None, kwargs=None, sync=False
):
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
    if sync:
        store.sync()
