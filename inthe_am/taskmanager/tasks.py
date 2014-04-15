from __future__ import absolute_import

from celery import shared_task

from .taskwarrior_client import TaskwarriorError
from .models import TaskStore


@shared_task
def sync_repository(store_id):
    store = TaskStore.objects.get(pk=store_id)
    try:
        store.sync(async=False)
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
