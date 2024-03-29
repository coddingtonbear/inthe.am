from contextlib import contextmanager
import logging
import os
import traceback
import uuid

from django.conf import settings
from django.utils.encoding import force_text

from .exceptions import NestedCheckpointError, InvalidTaskwarriorConfiguration
from .lock import get_lock_name_for_store, redis_lock


logger = logging.getLogger(__name__)


@contextmanager
def git_checkpoint(
    store,
    sourcetype: int,
    message: str,
    foreign_id: str = None,
    function=None,
    args=None,
    kwargs=None,
    sync=None,
    gc=False,
    notify_rollback=True,
    emit_announcements=True,
    data=None,
    wait_timeout=settings.LOCKFILE_WAIT_TIMEOUT,
    lock_timeout=settings.LOCKFILE_TIMEOUT_SECONDS,
):
    from .models import Change, ChangeSource, Task

    lock_name = get_lock_name_for_store(store)
    try:
        pre_work_sha = store.repository.head().decode("utf-8")
    except KeyError:
        pre_work_sha = None
    checkpoint_id = uuid.uuid4()

    if hasattr(store, "_active_checkpoint"):
        exception_message = (
            f"Store {store} attempted to acquire a checkpoint for "
            f"'{message}', but the repository was already locked for "
            f"'{store._active_checkpoint}'"
        )
        raise NestedCheckpointError(exception_message)
    store._active_checkpoint = message

    start_head = None
    end_head = None
    with redis_lock(
        lock_name,
        message=message,
        lock_timeout=lock_timeout,
        wait_timeout=wait_timeout,
    ):
        start_head = store.repository.head().decode("utf-8")
        git_index_lock_path = os.path.join(store.local_path, ".git/index.lock")
        if os.path.exists(os.path.join(store.local_path, ".git/index.lock")):
            try:
                os.remove(git_index_lock_path)
                logger.warning(
                    "Git repository at %s was found locked after acquiring "
                    "task repository lock; removing lock.",
                    store.local_path,
                )
            except Exception:
                logger.exception(
                    "Error encountered while cleaning-up git index lock at %s",
                    git_index_lock_path,
                )

        if not ChangeSource.objects.filter(
            store=store,
            sourcetype=ChangeSource.SOURCETYPE_BACKFILL,
        ).exists():
            Task.backfill_task_records(store)

        store.create_git_repository()
        try:
            store.create_git_checkpoint(
                message,
                function=function,
                args=args,
                kwargs=kwargs,
                pre_operation=True,
                checkpoint_id=checkpoint_id,
                data=data,
            )
            yield
            # We need to force taskw to garbage collect after engaging
            # in operations that might alter the task ID#s, otherwise
            # they'll hang out as uncommitted changes until the next
            # writing operation.
            if gc:
                store.client.gc()
            # We do not need to store undo.data since we're handling
            # history using a git repo and can revert using that.
            undo_path = os.path.join(store.local_path, "undo.data")
            if os.path.isfile(undo_path):
                os.unlink(undo_path)
            store.create_git_checkpoint(
                message,
                function=function,
                args=args,
                kwargs=kwargs,
                checkpoint_id=checkpoint_id,
                data=data,
            )

            end_head = store.repository.head().decode("utf-8")
            recurring_task_found = False

            source = ChangeSource.objects.create(
                sourcetype=sourcetype,
                store=store,
                foreign_id=foreign_id,
                commit_hash=end_head,
            )

            for task_id, changes in store.get_changed_tasks(
                end_head, start=start_head
            ).items():
                for field, values in changes.items():
                    Change.record_changes(source, task_id, field, values[0], values[1])

                task = store.client.get_task(uuid=task_id)[1]

                Task.record_change(
                    store,
                    source,
                    task.serialized(),
                )

                store.send_rest_hook_messages(task_id)
                if emit_announcements:
                    store.publish_announcement(
                        "changed_task",
                        {
                            "username": store.user.username,
                            "start": start_head,
                            "head": end_head,
                            "task_id": task_id,
                            "task_data": dict(task),
                            "changes": changes,
                        },
                    )
                if store.auto_deduplicate and task.get("recur"):
                    recurring_task_found = True

            if recurring_task_found:
                store.deduplicate_tasks()

            source.mark_finished()
            source.save()
        except InvalidTaskwarriorConfiguration:
            # A checkpoint will be created during account initialization;
            # if so, the taskwarrior client may not yet be configured.
            pass
        except Exception as e:
            store.create_git_checkpoint(
                f"{message} ({force_text(e, errors='replace')})",
                function=function,
                args=args,
                kwargs=kwargs,
                rollback=True,
            )
            dangling_sha = store.repository.head().decode("utf-8")
            changes_were_stored = dangling_sha and dangling_sha != pre_work_sha

            # Create a second checkpoint, and force the commit to occur
            # so we have a nice traceback.
            store.create_git_checkpoint(
                traceback.format_exc(),
                function=function,
                args=args,
                kwargs=kwargs,
                rollback=False,
                force_commit=True,
            )
            dangling_sha = store.repository.head().decode("utf-8")

            if changes_were_stored:
                logger.exception(
                    "An error occurred that required rolling-back "
                    "the git repository at %s from %s to %s.",
                    store.local_path,
                    dangling_sha,
                    pre_work_sha,
                )
                if notify_rollback:
                    store.log_error(
                        "An error occurred while interacting with your "
                        "task list, and your task list was recovered by "
                        "rolling-back to the last known good state (%s).  "
                        "Since your task list is synchronized with a "
                        "taskd server, this will likely not have any "
                        "negative effects.  Rollback ID: %s.",
                        pre_work_sha,
                        dangling_sha,
                    )
                store.git_reset(pre_work_sha)
            else:
                logger.exception(
                    "An error occurred that did not require rolling-back "
                    "the git repository at %s (at %s)",
                    store.local_path,
                    pre_work_sha,
                )
            raise

    delattr(store, "_active_checkpoint")

    if sync is True:
        store.sync()
    elif sync is None and start_head and end_head:
        changed_task_ids = store.get_changed_task_ids(end_head, start=start_head)
        if changed_task_ids:
            store.sync()
