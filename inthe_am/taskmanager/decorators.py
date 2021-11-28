from functools import wraps

from django.core.exceptions import PermissionDenied

from inthe_am.taskmanager.models.changesource import ChangeSource

from . import models
from .context_managers import git_checkpoint


def process_authentication(required=True):
    def authenticate(f):
        @wraps(f)
        def wrapper(self, request, *args, **kwargs):
            self._meta.authentication.is_authenticated(request)
            if required and not request.user.is_authenticated():
                raise PermissionDenied()
            return f(self, request, *args, **kwargs)

        return wrapper

    return authenticate


def requires_task_store(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated():
            raise PermissionDenied()

        store = models.TaskStore.get_for_user(request.user)
        kwargs["store"] = store
        result = f(self, *args, **kwargs)
        return result

    return wrapper


def git_managed(
    message,
    sync=False,
    gc=True,
    sourcetype: int = ChangeSource.SOURCETYPE_DIRECT,
    foreign_id=None,
):
    def git_sync(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            try:
                user = args[0].user
            except IndexError:
                # Tastypie Views
                user = kwargs["bundle"].request.user

            if not user.is_authenticated():
                raise PermissionDenied()

            store = models.TaskStore.get_for_user(user)
            kwargs["store"] = store
            with git_checkpoint(
                store,
                sourcetype,
                message,
                function=f.__name__,
                args=args[1:],
                kwargs=kwargs,
                sync=sync,
                gc=gc,
                foreign_id=foreign_id,
            ):
                result = f(self, *args, **kwargs)
            return result

        return wrapper

    return git_sync
