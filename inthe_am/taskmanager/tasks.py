from __future__ import absolute_import

from celery import shared_task

from taskw.exceptions import TaskwarriorError

from .context_managers import git_checkpoint


@shared_task
def sync_repository(store):
    try:
        with git_checkpoint(store, 'Synchronization'):
            store.client.sync()
    except TaskwarriorError as e:
        store.log_error(
            "Error while syncing tasks! "
            "Err. Code: %s; "
            "Std. Error: %s; "
            "Std. Out: %s.",
            e.code,
            e.stderr,
            e.stdout,
        )
