from __future__ import absolute_import

from celery import shared_task


@shared_task
def sync_repository(store_id):
    from .models import TaskStore
    store = TaskStore.objects.get(pk=store_id)
    store.sync(
        async=False,
        function='tasks.sync_repository',
        args=(store_id, ),
    )
