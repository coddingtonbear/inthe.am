from contextlib import contextmanager
import os

from lockfile.pidlockfile import PIDLockFile


@contextmanager
def git_checkpoint(store, message, function=None, args=None, kwargs=None, sync=False):
    if sync:
        store.sync()
    with PIDLockFile(os.path.join(store.local_path, '.lock')):
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
    if sync:
        store.sync()
