import json

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponse

from ..lock import LockTimeout
from ..taskwarrior_client import TaskwarriorError
from .. import models


class LockTimeoutMixin(object):
    def _handle_500(self, request, e):
        if isinstance(e, TaskwarriorError):
            # Note -- this error message will be printed to the USER's
            # error log regardless of whether or not the error that occurred
            # was a problem with their task list, or that of a Kanban board.
            store = models.TaskStore.get_for_user(request.user)
            message = '(%s) %s' % (
                e.code,
                e.stderr,
            )
            store.log_silent_error(
                'Taskwarrior Error: %s' % message
            )
            return HttpResponse(
                json.dumps(
                    {
                        'error_message': message
                    }
                ),
                content_type='application/json',
                status=400,
            )
        elif isinstance(e, LockTimeout):
            message = (
                'Your task list is currently in use; please try again later.'
            )
            store = models.TaskStore.get_for_user(request.user)
            store.log_error(message)
            return HttpResponse(
                json.dumps(
                    {
                        'error_message': message
                    }
                ),
                content_type='application/json',
                status=409,
            )
        elif isinstance(e, PermissionDenied):
            return HttpResponse(
                json.dumps(
                    {
                        'error_message': 'Unauthorized',
                    }
                ),
                content_type='application/json',
                status=401,
            )
        elif isinstance(e, ObjectDoesNotExist):
            return HttpResponse(
                json.dumps(
                    {
                        'error_message': 'Resource Not Found',
                    }
                ),
                content_type='application/json',
                status=404,
            )
        return super(LockTimeoutMixin, self)._handle_500(request, e)
