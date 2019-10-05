from __future__ import absolute_import

from fnmatch import fnmatch as glob
import json
import logging
import re
import shlex

from celery import shared_task
from celery.signals import setup_logging
from django.conf import settings
from django.utils.timezone import now
from django_mailbox.models import Message
import requests
from rest_framework.renderers import JSONRenderer

from .context_managers import git_checkpoint
from .lock import get_debounce_name_for_store, get_lock_redis, LockTimeout
from .merge_tasks import merge_all_duplicate_tasks
from .serializers.task import TaskSerializer


logger = logging.getLogger(__name__)


@setup_logging.connect
def project_setup_logging(loglevel, logfile, format, colorize, **kwargs):
    import logging.config
    from django.conf import settings
    logging.config.dictConfigClass(settings.LOGGING).configure()


@shared_task(
    bind=True,
)
def autoconfigure_taskd(self, store_id):
    from .models import TaskStore
    store = TaskStore.objects.get(pk=store_id)

    try:
        if not store.configured:
            store.autoconfigure_taskd()
    except:
        if not settings.DEBUG:
            raise
        message = "Error encountered while configuring task store."
        logger.exception(message)
        store.log_error(message)


@shared_task(
    bind=True,
    time_limit=120,
    default_retry_delay=120,
    max_retries=10,
)
def sync_repository(self, store_id, debounce_id=None, **kwargs):
    from .models import TaskStore
    store = TaskStore.objects.get(pk=store_id)
    try:
        store.sync(
            asynchronous=False,
            function='tasks.sync_repository',
            args=(store_id, ),
            kwargs={'debounce_id': debounce_id},
        )
    except Exception as e:
        raise self.retry(exc=e)


@shared_task(
    bind=True,
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
                params = arg.split('=')
                if params[0] == 'priority':
                    params[1] = params[1].upper()
                args.append('%s:"%s"' % tuple(params))
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
        with git_checkpoint(store, 'Incoming E-mail'):
            task_args = [
                'add',
                'intheamoriginalemailsubject:"%s"' % message.subject,
                'intheamoriginalemailid:%s' % message.pk,
            ] + additional_args + shlex.split(
                message.text.split('\n\n')[0]  # Only use text up to the first
                                               # blank line.
            )
            stdout, stderr = store.client._execute_safe(*task_args)
            task = store.client.get_task(intheamoriginalemailid=message.pk)[1]
            task_id = str(task['uuid'])

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
    default_retry_delay=60,
    max_retries=1,
)
def reset_trello(self, store_id, **kwargs):
    from .models import TaskStore, TrelloObject
    store = TaskStore.objects.get(pk=store_id)

    for obj in TrelloObject.objects.filter(store=store):
        obj.delete()

    store.trello_auth_token = ''
    store.trello_local_head = ''
    store.save()

    with git_checkpoint(
        store, "Reset trello IDs for pending/waiting tasks."
    ):
        for task in store.client.filter_tasks({
            'intheamtrelloid.any': None,
            'or': [
                ('status', 'pending'),
                ('status', 'waiting'),
            ]
        }):
            task['intheamtrelloid'] = ''
            task['intheamtrelloboardid'] = ''
            task['intheamtrellolistid'] = ''
            store.client.task_update(task)

    store.publish_personal_announcement({
        'title': 'Trello',
        'message': 'Trello has been successfully reset.'
    })


@shared_task(
    bind=True,
    default_retry_delay=60,
    max_retries=10,
)
def sync_trello_tasks(self, store_id, debounce_id=None, **kwargs):
    from .models import TaskStore, TrelloObject
    store = TaskStore.objects.get(pk=store_id)
    client = get_lock_redis()

    starting_head = store.repository.head().decode('utf-8')

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

    with git_checkpoint(store, 'Reconciling trello board', sync=False):
        store.trello_board.reconcile()

    open_local_tasks = {
        t['uuid']: t for t in store.client.filter_tasks({
            'status': 'pending'
        })
    }
    with git_checkpoint(
        store, 'Deleting non-pending tasks from trello', sync=False
    ):
        for task in store.client.filter_tasks({
            'intheamtrelloid.any': None,
            'or': [
                ('status', 'waiting'),
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
        'Adding pending tasks to Trello & deleting tasks remotely deleted',
        sync=False,
    ):
        todo_column = store.trello_board.get_list_by_type(TrelloObject.TO_DO)
        for task in open_local_tasks.values():
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
                    idList=todo_column.id,
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

    with git_checkpoint(
        store,
        'Reconcile all known trello tasks.',
        sync=False,
    ):
        for task in to_reconcile:
            task.reconcile()

    with git_checkpoint(
        store,
        'Add local tasks to match tasks created in Trello',
        sync=False,
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

    ending_head = store.repository.head().decode('utf-8')
    store.trello_local_head = ending_head
    store.save()

    if store.get_changed_task_ids(ending_head, start=starting_head):
        store.sync()

    store.publish_personal_announcement({
        'title': 'Trello',
        'message': 'Synchronization completed successfully.'
    })


@shared_task(
    bind=True,
    default_retry_delay=30,
    max_retries=10,
)
def process_trello_action(self, store_id, data, **kwargs):
    from .models import TaskStore, TrelloObject, TrelloObjectAction
    store = TaskStore.objects.get(pk=store_id)

    try:
        with git_checkpoint(store, 'Processing Trello Action', data=data):
            try:
                TrelloObjectAction.create_from_request(data)
            except TrelloObject.DoesNotExist:
                pass
    except LockTimeout as e:
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    default_retry_delay=30,
    max_retries=10,
)
def update_trello(
    self, store_id, debounce_id=None, current_head=None, **kwargs
):
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

    ending_head = store.repository.head().decode('utf-8')
    starting_head = store.trello_local_head
    changed_ids = store.get_changed_task_ids(
        ending_head,
        start=starting_head
    )
    with git_checkpoint(
        store,
        "Create trello records for changed tasks.",
        data=changed_ids,
    ):
        todo_column = store.trello_board.get_list_by_type(TrelloObject.TO_DO)

        for task_id in changed_ids:
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
                continue

            # Do not send recurring tasks to trello
            if task['status'] == 'recurring':
                continue

            try:
                obj = TrelloObject.objects.get(pk=task.get('intheamtrelloid'))
            except TrelloObject.DoesNotExist:
                if task.get('intheamtrelloid'):
                    logger.warning(
                        "Unable to update task %s; assigned trello object "
                        " %s is not tracked.  This should not happen.",
                        task.get('uuid'),
                        task.get('intheamtrelloid'),
                        extra={
                            'stack': True,
                        }
                    )
                    continue

                # If we are going to have to create this task, only do that
                # if the task is currently open.
                if task['status'] != 'pending':
                    continue

                obj = TrelloObject.create(
                    store=store,
                    type=TrelloObject.CARD,
                    name=task['description'],
                    idList=todo_column.id
                )
                result = obj.client_request(
                    'PUT',
                    '/1/cards/%s/pos' % obj.id,
                    data={'value': 'top'},
                )
                if not (200 <= result.status_code < 300):
                    logger.warning(
                        "Unable to set card position: %s",
                        result.content,
                        extra={
                            'data': {
                                'result': result.json(),
                            }
                        }
                    )
                task['intheamtrelloid'] = obj.pk
                task['intheamtrelloboardid'] = store.trello_board.pk

            # Try changing lists, too, if requested
            if task.get('intheamtrellolistname'):
                try:
                    list_requested = obj.store.trello_board.get_list_by_type(
                        task.get('intheamtrellolistname')
                    )
                    if list_requested.pk != task.get('intheamtrellolistid'):
                        task['intheamtrellolistid'] = list_requested.pk
                except TrelloObject.DoesNotExist:
                    try:
                        list_actual = obj.store.trello_board.children.get(
                            id=task.get('intheamtrellolistid')
                        )
                        task['intheamtrellolistname'] = list_actual.meta.get(
                            'name'
                        )
                    except TrelloObject.DoesNotExist:
                        task['intheamtrellolistid'] = todo_column.pk
                        task['intheamtrellolistname'] = todo_column.meta.get(
                            'name'
                        )

            try:
                obj.update_trello(task)
            except Exception as e:
                logger.exception(
                    "Error encountered while updating task: %s",
                    str(e)
                )

            # Clear trello ID if we've just marked the task as closed;
            # this will cause us to re-create the record if it ever
            # enters the "pending" status.
            if task['status'] in ('waiting', 'closed', 'deleted'):
                task['intheamtrelloid'] = ''

            store.client.task_update(task)

        store.trello_local_head = ending_head
        store.save()


@shared_task(
    bind=True,
    default_retry_delay=30,
    max_retries=10,
)
def deduplicate_tasks(self, store_id, debounce_id=None, **kwargs):
    from .models import TaskStore
    store = TaskStore.objects.get(pk=store_id)

    client = get_lock_redis()

    debounce_key = get_debounce_name_for_store(store, 'deduplication')
    try:
        expected_debounce_id = client.get(debounce_key)
    except (ValueError, TypeError):
        expected_debounce_id = None

    if (
        expected_debounce_id and debounce_id and
        (float(debounce_id) < float(expected_debounce_id))
    ):
        logger.warning(
            'Deduplication debounce failed: %s<%s for %s.',
            debounce_id,
            expected_debounce_id,
            store.pk,
        )
        return

    with git_checkpoint(store, 'Deduplicate tasks'):
        results = merge_all_duplicate_tasks(store)

        for alpha, betas in results.items():
            store.log_message(
                "Tasks %s merged into %s.",
                ', '.join([str(b) for b in betas]),
                str(alpha),
            )

    store.publish_personal_announcement({
        'title': 'Deduplication',
        'message': 'Deduplication process completed successfully.'
    })


@shared_task(
    bind=True,
    default_retry_delay=15,
    max_retries=10,
)
def send_rest_hook_message(self, rest_hook_id, task_id, **kwargs):
    from . import models

    rest_hook = models.RestHook.objects.get(id=rest_hook_id)
    task_data = rest_hook.task_store.client.get_task(uuid=task_id)[1]

    result = requests.post(
        rest_hook.target_url,
        data=JSONRenderer().render(
            TaskSerializer(task_data, store=rest_hook.task_store).data
        ),
        headers={
            'Content-type': 'application/json',
        }
    )
    if result.status_code == 410:
        rest_hook.delete()
        return

    result.raise_for_status()
