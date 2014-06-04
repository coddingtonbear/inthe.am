from __future__ import absolute_import

import logging
import shlex
import uuid

from celery import shared_task
from django_mailbox.models import Message


logger = logging.getLogger(__name__)


@shared_task
def sync_repository(store_id):
    from .models import TaskStore
    store = TaskStore.objects.get(pk=store_id)
    store.sync(
        async=False,
        function='tasks.sync_repository',
        args=(store_id, ),
    )


@shared_task
def process_email_message(message_id):
    from .models import TaskStore
    message = Message.objects.get(pk=message_id)

    store = None
    for address in message.to_addresses:
        try:
            store = TaskStore.objects.get(
                secret_id=address.split('@')[0]
            )
            break
        except TaskStore.DoesNotExist:
            pass

    if not store:
        logger.error(
            "Could not find task store for e-mail message (ID %s) addressed "
            "to %s",
            message.pk,
            message.to_addresses
        )

    if (
        not message.subject
        or message.subject.lower() in ['add', 'create', 'new'],
    ):
        task_id = str(uuid.uuid4())
        task_args = [
            'add',
            'uuid:%s' % task_id,
            'intheamoriginalemailsubject:"%s"' % message.subject,
            'intheamoriginalemailid:%s' % message.pk,
        ] + shlex.split(message.text)

        stdout, stderr = store.client._execute_safe(*task_args)

        import ipdb
        ipdb.set_trace()


        log_args = (
            "Added task %s via e-mail %s from %s." % (
                task_id,
                message.pk,
                message.from_address[0]
            ),
        )
        logger.info(*log_args)
        store.log_message(*log_args)
    else:
        log_args = (
            "Unable to process e-mail %s from %s; unknown subject '%s'" % (
                message.pk,
                message.from_address[0],
                message.subject,
            ),
        )
        logger.info(*log_args)
        store.log_message(*log_args)
