from __future__ import absolute_import

from fnmatch import fnmatch as glob
import logging
import re
import shlex
import uuid

from celery import shared_task
from celery.signals import setup_logging
from django.conf import settings
from django.utils.timezone import now
from django_mailbox.models import Message

from .context_managers import git_checkpoint
from .lock import get_debounce_name_for_store, get_lock_redis


logger = logging.getLogger(__name__)


@setup_logging.connect
def project_setup_logging(loglevel, logfile, format, colorize, **kwargs):
    import logging.config
    from django.conf import settings
    logging.config.dictConfigClass(settings.LOGGING).configure()


@shared_task(
    bind=True,
    soft_time_limit=30,
    time_limit=45,
    default_retry_delay=60,
    max_retries=10,  # We should always stop at two, anyway
    ignore_result=True,
)
def sync_repository(self, store_id, debounce_id=None):
    from .models import TaskStore
    store = TaskStore.objects.get(pk=store_id)
    try:
        store.sync(
            async=False,
            function='tasks.sync_repository',
            args=(store_id, ),
            kwargs={'debounce_id': debounce_id},
        )
    except Exception as e:
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    ignore_result=True,
)
def process_email_message(self, message_id):
    from .models import TaskAttachment, TaskStore

    with open('/tmp/out.log', 'w') as out:
        import json
        out.write(
            json.dumps(settings.LOGGING, indent=4)
        )
        out.write(__name__)

    def get_secret_id_and_args(address):
        inbox_id = address[0:36]
        args = []

        arg_string = address[36:]
        for arg in re.split('__|\+', arg_string):
            if not arg:
                continue
            if '=' in arg:
                args.append(
                    '%s:"%s"' % tuple(arg.split('='))
                )
            else:
                args.append('+%s' % arg)

        return inbox_id, args

    message = Message.objects.get(pk=message_id)
    message.read = now()
    message.save()

    store = None
    additional_args = []
    # Check for matching To: addresses.
    for address in message.to_addresses:
        try:
            inbox_id, additional_args = get_secret_id_and_args(
                address.split('@')[0]
            )

            store = TaskStore.objects.get(
                secret_id=inbox_id
            )
            break
        except (TaskStore.DoesNotExist, IndexError):
            pass

    # Check for 'Received' headers matching a known e-mail address.
    if store is None:
        email_regex = re.compile(r'([0-9a-fA-F-]{36}@inthe.am)')
        all_received_headers = message.get_email_object().get_all('Received')
        for header in all_received_headers:
            matched_email = email_regex.search(header)
            if matched_email:
                address = matched_email.group(1)
                try:
                    inbox_id, additional_args = get_secret_id_and_args(
                        address.split('@')[0]
                    )

                    store = TaskStore.objects.get(
                        secret_id=inbox_id
                    )
                    break
                except (TaskStore.DoesNotExist, IndexError):
                    pass

    if store is None:
        logger.error(
            "Could not find task store for e-mail message (ID %s) addressed "
            "to %s",
            message.pk,
            message.to_addresses
        )
        return

    allowed = False
    for address in store.email_whitelist.split('\n'):
        if glob(message.from_address[0], address):
            allowed = True

    if not allowed:
        log_args = (
            "Incoming task creation e-mail (ID: %s) from '%s' "
            "does not match email whitelist and was ignored." % (
                message.pk,
                message.from_address[0]
            ),
        )
        logger.info(*log_args)
        store.log_message(*log_args)
        return

    if (
        not message.subject
        or message.subject.lower() in ['add', 'create', 'new'],
    ):
        task_id = str(uuid.uuid4())
        with git_checkpoint(store, 'Incoming E-mail'):
            task_args = [
                'add',
                'uuid:%s' % task_id,
                'intheamoriginalemailsubject:"%s"' % message.subject,
                'intheamoriginalemailid:%s' % message.pk,
            ] + additional_args + shlex.split(
                message.text.split('\n\n')[0]  # Only use text up to the first
                                               # blank line.
            )
            stdout, stderr = store.client._execute_safe(*task_args)
            task = store.client.get_task(uuid=task_id)[1]

            attachment_urls_raw = task.get('intheamattachments')
            if not attachment_urls_raw:
                attachment_urls = []
            else:
                attachment_urls = attachment_urls_raw.split('|')

            for record in message.attachments.all():
                attachment = record.document
                if attachment.file.size > settings.FILE_UPLOAD_MAXIMUM_BYTES:
                    logger.info(
                        "File %s too large (%s bytes).",
                        attachment.file.name,
                        attachment.file.size,
                    )
                    store.log_message(
                        "Attachments must be smaller than %s "
                        "bytes to be saved to a task, but the "
                        "attachment %s received for task ID %s "
                        "is %s bytes in size and was not saved "
                        "as a result." % (
                            settings.FILE_UPLOAD_MAXIMUM_BYTES,
                            attachment.file.name,
                            task_id,
                            attachment.file.size,
                        )
                    )
                    attachment.delete()
                    continue

                document = TaskAttachment.objects.create(
                    store=store,
                    task_id=task_id,
                    name=record.get_filename(),
                    size=attachment.file.size,
                )
                document.document.save(
                    record.get_filename(),
                    attachment.file,
                )
                attachment_urls.append(
                    document.document.url
                )
                store.client.task_annotate(
                    task, 'Attached File: %s' % document.document.url
                )

            if attachment_urls:
                task['intheamattachments'] = ' '.join(attachment_urls)
                store.client.task_update(task)

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


@shared_task(
    bind=True,
    ignore_result=True,
    max_retries=10,
    default_retry_delay=60,
)
def sync_trello_tasks(self, store_id, debounce_id=None):
    from .models import TaskStore, TrelloObject
    store = TaskStore.objects.get(pk=store_id)
    client = get_lock_redis()

    starting_head = store.repository.head()

    debounce_key = get_debounce_name_for_store(store, 'trello')
    try:
        expected_debounce_id = client.get(debounce_key)
    except (ValueError, TypeError):
        expected_debounce_id = None

    if (
        expected_debounce_id and debounce_id and
        (float(debounce_id) < float(expected_debounce_id))
    ):
        logger.warning(
            "Trello Debounce Failed: %s<%s; "
            "skipping trello synchronization for %s",
            debounce_id,
            expected_debounce_id,
            store.pk,
        )
        return

    if not store.trello_auth_token:
        logger.warning(
            "'sync_trello_tasks' task received, but no Trello auth token "
            "is available!",
            extra={
                'stack': True,
            }
        )
        return

    store.trello_board.reconcile()

    open_local_tasks = {
        t['uuid']: t for t in store.client.filter_tasks({
            'or': [
                ('status', 'pending'),
                ('status', 'waiting'),
            ]
        })
    }
    with git_checkpoint(store, 'Deleting non-pending tasks from trello'):
        for task in store.client.filter_tasks({
            'intheamtrelloid.any': None,
            'or': [
                ('status', 'completed'),
                ('status', 'deleted'),
            ],
        }):
            try:
                tob = TrelloObject.objects.get(
                    id=task['intheamtrelloid'],
                    store=store,
                )
                tob.delete()
            except TrelloObject.DoesNotExist:
                pass

    open_trello_cards = {
        c['id']: c for c in store.trello_board.client.get_card_filter(
            'open',
            store.trello_board.id,
        )
    }
    to_reconcile = []
    with git_checkpoint(
        store,
        'Adding pending tasks to Trello & deleting tasks remotely deleted'
    ):
        todo_column = store.trello_board.get_list_by_type(TrelloObject.TO_DO)
        wait_column = store.trello_board.get_list_by_type(TrelloObject.WAITING)
        for task in open_local_tasks.values():
            is_pending = task.get('status') == 'pending'

            # If this task has a trello board ID, but it doesn't match the
            # board we're currently on, let's pretend that it doesn't have
            # an id at all -- it was probably un-deleted or restored
            task_board_id = task.get('intheamtrelloboardid')
            if task_board_id and task_board_id != store.trello_board.id:
                task['intheamtrelloid'] = ''

            if not task.get('intheamtrelloid'):
                tob = TrelloObject.create(
                    store=store,
                    type=TrelloObject.CARD,
                    name=task['description'],
                    idList=todo_column.id if is_pending else wait_column.id,
                )
                task['intheamtrelloid'] = tob.id
                task['intheamtrelloboardid'] = store.trello_board.id
                store.client.task_update(task)

                to_reconcile.append(tob)
            else:
                res = open_trello_cards.pop(task.get('intheamtrelloid'), None)
                if res is None:
                    store.client.task_done(uuid=task.get('uuid'))
                    continue

                try:
                    tob = TrelloObject.objects.get(
                        id=task['intheamtrelloid'],
                        store=store,
                    )
                    tob.meta = res
                    tob.save()
                    to_reconcile.append(tob)
                except TrelloObject.DoesNotExist:
                    logging.exception(
                        "Attempted to update card status but card "
                        "was not found in database!"
                    )

    for task in to_reconcile:
        task.reconcile()

    with git_checkpoint(
        store,
        'Add local tasks to match tasks created in Trello'
    ):
        for task in open_trello_cards.values():
            name = task.get('name')
            id = task.get('id')

            tob = TrelloObject.objects.create(
                id=id,
                store=store,
                type=TrelloObject.CARD,
                meta=task,
            )
            tob.subscribe()
            data = {
                'description': name,
                'intheamtrelloid': id,
                'intheamtrelloboardid': store.trello_board.id,
            }
            store.client.task_add(**data),

    ending_head = store.repository.head()
    store.trello_local_head = ending_head
    store.save()

    if store.get_changed_task_ids(ending_head, start=starting_head):
        store.sync()


@shared_task(
    bind=True,
    ignore_result=True,
)
def process_trello_action(self, store_id, data):
    from .models import TrelloObjectAction

    action = TrelloObjectAction.create_from_request(data)


@shared_task(
    bind=True,
    ignore_result=True,
    max_retries=10,
    default_retry_delay=15
)
def update_trello(self, store_id, debounce_id=None):
    from .models import TaskStore, TrelloObject
    store = TaskStore.objects.get(pk=store_id)
    client = get_lock_redis()

    debounce_key = get_debounce_name_for_store(store, 'trello_outgoing')
    try:
        expected_debounce_id = client.get(debounce_key)
    except (ValueError, TypeError):
        expected_debounce_id = None

    if (
        expected_debounce_id and debounce_id and
        (float(debounce_id) < float(expected_debounce_id))
    ):
        logger.warning(
            "Trello Outgoing Debounce Failed: %s<%s; "
            "skipping trello outgoing updates for %s",
            debounce_id,
            expected_debounce_id,
            store.pk,
        )
        return

    ending_head = store.repository.head()
    starting_head = store.trello_local_head

    todo_column = store.trello_board.get_list_by_type(TrelloObject.TO_DO)
    requires_post_sync = False
    for task_id in store.get_changed_task_ids(
        ending_head,
        start=starting_head
    ):
        try:
            task = store.client.filter_tasks({
                'uuid': task_id,
            })[0]
        except IndexError:
            logger.exception(
                "Attempted to update task object for {trello_id}, "
                "but no matching tasks were found in the store!".format(
                    trello_id=task_id,
                )
            )
            return

        try:
            obj = TrelloObject.objects.get(pk=task['intheamtrelloid'])
        except TrelloObject.DoesNotExist:
            obj = TrelloObject.create(
                store=store,
                type=TrelloObject.CARD,
                name=task['description'],
                idList=todo_column.id
            )
            with git_checkpoint(store, "Create trello record for task."):
                task['intheamtrelloid'] = obj.pk
                task['intheamtrelloboardid'] = store.trello_board.pk
                store.client.task_update(task)
                requires_post_sync = True

        obj.update_trello(task)

    store.trello_local_head = ending_head
    store.save()

    if requires_post_sync:
        store.sync()
