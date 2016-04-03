from functools import wraps

from django.core.exceptions import PermissionDenied

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
        try:
            # Some Tastypie Views
            request = args[0].request
        except AttributeError:
            # Normal Views
            request = args[0]
        except IndexError:
            # Other Tastypie Views
            request = kwargs['bundle'].request

        if not request.user.is_authenticated():
            raise PermissionDenied()

        store = models.TaskStore.get_for_user(request.user)
        kwargs['store'] = store
        result = f(self, *args, **kwargs)
        return result
    return wrapper


def git_managed(message, sync=False, gc=True):
    def git_sync(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            try:
                user = args[0].user
            except IndexError:
                # Tastypie Views
                user = kwargs['bundle'].request.user

            if not user.is_authenticated():
                raise PermissionDenied()

            store = models.TaskStore.get_for_user(user)
            kwargs['store'] = store
            with git_checkpoint(
                store, message, f.__name__, args[1:], kwargs, sync=sync, gc=gc
            ):
                result = f(self, *args, **kwargs)
            return result
        return wrapper
    return git_sync
