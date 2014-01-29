from functools import wraps

from . import models


def requires_taskd_sync(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            # Normal Views
            user = args[0].user
        except IndexError:
            # Tastypie Views
            user = kwargs['bundle'].request.user
        store = models.TaskStore.get_for_user(user)
        kwargs['store'] = store
        store.sync()
        result = f(self, *args, **kwargs)
        store.sync()
        return result
    return wrapper


def git_checkpoint(message):
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
            store.create_git_checkpoint(
                message,
                function=f.__name__,
                args=args,
                kwargs=kwargs,
                pre_operation=True,
            )
            result = f(self, *args, **kwargs)
            store.create_git_checkpoint(
                message,
                function=f.__name__,
                args=args,
                kwargs=kwargs
            )
            return result
        return wrapper
    return git_sync
