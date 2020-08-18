import json
import logging

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.exceptions import (
    ObjectDoesNotExist,
    PermissionDenied,
    SuspiciousOperation,
)
from django.urls import reverse
from django.http import (
    Http404,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .lock import LockTimeout
from .models import TaskStore, RestHook
from .taskwarrior_client import TaskwarriorError


logger = logging.getLogger(__name__)


class TaskFeed(Feed):
    def get_object(self, request, uuid):
        try:
            store = TaskStore.objects.get(secret_id=uuid)
        except TaskStore.DoesNotExist:
            raise Http404()

        if not store.feed_enabled:
            raise Http404()

        return store

    def item_title(self, item):
        return item.get("description")

    def item_description(self, item):
        lines = []
        for k, v in item.items():
            lines.append(u"{k}: {v}".format(k=k, v=v))
        return "\n".join(lines)

    def item_link(self, item):
        return u"/tasks/{uuid}".format(uuid=item.get("uuid"))

    def items(self, store):
        tasks = store.client.filter_tasks({"status": "pending", "limit": "100"})
        tasks = sorted(tasks, key=lambda d: float(d["urgency"]), reverse=True)
        return tasks

    def description(self, store):
        return (
            u"Highest urgency tasks on {first_name} {last_name}'s "
            "task list.".format(
                first_name=store.user.first_name, last_name=store.user.last_name
            )
        )

    def link(self, store):
        return reverse("feed", kwargs={"uuid": store.secret_id})

    def title(self, store):
        return u"{first_name} {last_name}'s tasks".format(
            first_name=store.user.first_name, last_name=store.user.last_name
        )


def debug_login(request):
    from inthe_am.taskmanager.debug_utils import artificial_login

    if not settings.DEBUG:
        raise SuspiciousOperation("Artificial login attempted while not in debug mode!")

    try:
        cookies = artificial_login(
            username=request.GET["username"], password=request.GET["password"],
        )
    except AttributeError:
        return HttpResponseBadRequest()
    response = HttpResponseRedirect("/")
    for name, value in cookies.items():
        response.set_cookie(name, value)
    return response


def rest_exception_handler(e, context):
    response = drf_exception_handler(e, context)
    request = context["request"]

    if isinstance(e, TaskwarriorError):
        # Note -- this error message will be printed to the USER's
        # error log regardless of whether or not the error that occurred
        # was a problem with their task list, or that of a Kanban board.
        store = TaskStore.get_for_user(request.user)
        message = "(%s) %s" % (e.code, e.stderr,)
        store.log_silent_error("Taskwarrior Error: %s" % message)
        return Response({"error_message": message}, status=400,)
    elif isinstance(e, LockTimeout):
        message = "Your task list is currently in use; please try again later."
        store = TaskStore.get_for_user(request.user)
        store.log_error(message)
        return Response(
            {
                "error_message": (
                    "Your task list is currently in use; please try " "again later."
                )
            },
            status=409,
        )
    elif isinstance(e, PermissionDenied):
        return Response(status=401)
    elif isinstance(e, ObjectDoesNotExist):
        return Response(status=404)
    else:
        return response


class RestHookHandler(View):
    http_method_names = ["delete", "post"]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        try:
            result = TokenAuthentication().authenticate(request)
            if not result:
                return JsonResponse({}, status=401)
            request.user, _ = result
        except AuthenticationFailed:
            return JsonResponse({}, status=403)

        return super(RestHookHandler, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({}, status=400)

        store = TaskStore.get_for_user(request.user)
        instance = RestHook.objects.create(
            task_store=store, event_type=data["event"], target_url=data["target_url"],
        )

        return JsonResponse({"id": instance.id,}, status=201)

    def delete(self, request, hook_id, *args, **kwargs):
        store = TaskStore.get_for_user(request.user)

        try:
            row = RestHook.objects.get(id=hook_id, task_store=store)
        except RestHook.DoesNotExist:
            return JsonResponse({}, status=404)

        row.delete()

        return JsonResponse({}, status=200)
