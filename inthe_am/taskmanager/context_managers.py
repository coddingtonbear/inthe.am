from contextlib import contextmanager
import logging
import os
import uuid

from .exceptions import NestedCheckpointError
from .lock import get_lock_name_for_store, redis_lock


logger = logging.getLogger(__name__)


@contextmanager
def git_checkpoint(
    store, message, function=None, args=None, kwargs=None,
    sync=False, gc=True, notify_rollback=True,
    emit_announcements=True,
):
    lock_name = get_lock_name_for_store(store)
    pre_work_sha = store.repository.head()
    checkpoint_id = uuid.uuid4()

    if(hasattr(store, '_active_checkpoint')):
        exception_message = (
            "Store %s attempted to acquire a checkpoint for '%s', but "
            "the repository was already locked for '%s'."
        ) % (
            store,
            message,
            store._active_checkpoint
        )
        raise NestedCheckpointError(exception_message)
    store._active_checkpoint = message

    with redis_lock(lock_name, message=message):
        start_head = store.repository.head()
        git_index_lock_path = os.path.join(
            store.local_path,
            '.git/index.lock'
        )
        if os.path.exists(
            os.path.join(
                store.local_path,
                '.git/index.lock'
            )
        ):
            try:
                os.remove(git_index_lock_path)
                logger.warning(
                    "Git repository at %s was found locked after acquiring "
                    "task repository lock; removing lock.",
                    store.local_path,
                )
            except:
                logger.exception(
                    "Error encountered while cleaning-up git index lock at %s",
                    git_index_lock_path,
                )

        store.create_git_repository()
        try:
            store.create_git_checkpoint(
                message,
                function=function,
                args=args,
                kwargs=kwargs,
                pre_operation=True,
                checkpoint_id=checkpoint_id,
            )
            yield
            # We need to force taskw to garbage collect after engaging
            # in operations that might alter the task ID#s, otherwise
            # they'll hang out as uncommitted changes until the next
            # writing operation.
            if gc:
                store.client.filter_tasks({'status': 'pending'})
            store.create_git_checkpoint(
                message,
                function=function,
                args=args,
                kwargs=kwargs,
                checkpoint_id=checkpoint_id,
            )

            end_head = store.repository.head()
            if emit_announcements:
                for task_id in store.get_changed_task_ids(
                    end_head, start=start_head
                ):
                    store.publish_announcement(
                        'changed_task',
                        {
                            'username': store.user.username,
                            'start': start_head,
                            'head': end_head,
                            'task_id': task_id,
                        }
                    )
        except Exception as e:
            store.create_git_checkpoint(
                str(e),
                function=function,
                args=args,
                kwargs=kwargs,
                rollback=True
            )
            dangling_sha = store.repository.head()
            changes_were_stored = (
                dangling_sha and dangling_sha != pre_work_sha
            )
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
                    "An error occured that did not require rolling-back "
                    "the git repository at %s (at %s)",
                    store.local_path,
                    pre_work_sha
                )
            raise

    delattr(store, '_active_checkpoint')

    if sync:
        store.sync()
