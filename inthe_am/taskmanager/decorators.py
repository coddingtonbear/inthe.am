from functools import wraps

from . import models
from .context_managers import git_checkpoint


def requires_task_store(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            # Normal Views
            user = args[0].user
        except AttributeError:
            # Some Tastypie Views
            user = args[0].request.user
        except IndexError:
            # Other Tastypie Views
            user = kwargs['bundle'].request.user

        store = models.TaskStore.get_for_user(user)
        kwargs['store'] = store
        result = f(self, *args, **kwargs)
        return result
    return wrapper


def git_managed(message, sync=False):
    def git_sync(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            try:
                user = args[0].user
            except IndexError:
                # Tastypie Views
                user = kwargs['bundle'].request.user
            store = models.TaskStore.get_for_user(user)
            kwargs['store'] = store
            with git_checkpoint(
                store, message, f.__name__, args[1:], kwargs, sync=sync
            ):
                result = f(self, *args, **kwargs)
            return result
        return wrapper
    return git_sync
