import datetime
import json
import logging
import re
import uuid

from django.contrib.auth.models import User
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseRedirect,
    JsonResponse
)
from django.views.decorators.csrf import csrf_exempt
from icalendar import Calendar, Event
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import (
    AllowAny, IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from twilio.util import RequestValidator
from twilio.twiml import Response as TwilioResponse

from .. import models
from ..context_managers import git_checkpoint, timed_activity
from ..decorators import git_managed, requires_task_store
from ..lock import get_lock_name_for_store, get_lock_redis
from ..serializers.task import TaskSerializer
from ..tasks import (
    deduplicate_tasks,
    process_trello_action,
    reset_trello,
    sync_trello_tasks,
)
from ..trello_utils import get_access_token, get_authorize_url
from ..utils import shlex_without_quotes


logger = logging.getLogger(__name__)


class TaskViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, )

    TASK_TYPE = 'pending'
    FILTERABLE_FIELDS = [
        'status',
        'due',
        'entry',
        'id',
        'imask',
        'modified',
        'parent',
        'recur',
        'status',
        'urgency',
        'uuid',
        'wait',
    ]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            metadata = models.UserMetadata.get_for_user(request.user)
        else:
            metadata = None
        if metadata and not metadata.tos_up_to_date:
            return JsonResponse(
                {
                    'error_message': (
                        'Please accept the terms of service at '
                        'https://inthe.am/terms-of-use.'
                    )
                },
                status=403
            )
        if metadata and not metadata.privacy_policy_up_to_date:
            return JsonResponse(
                {
                    'error_message': (
                        'Please accept the privacy policy at '
                        'https://inthe.am/privacy-policy.'
                    )
                },
                status=403
            )
        return super(TaskViewSet, self).dispatch(request, *args, **kwargs)

    def passes_filters(self, task, filters):
        passes = True
        for key, value in filters.items():
            if key not in self.FILTERABLE_FIELDS:
                continue
            task_value = getattr(task, key, None)
            if task_value != value:
                passes = False
        return passes

    @requires_task_store
    def list(self, request, store=None):
        if hasattr(request, 'GET'):
            filters = request.GET.copy()

        objects = []
        with timed_activity(store, 'Get task list'):
            for task_object in store.client.filter_tasks(
                {'status': self.TASK_TYPE}
            ):
                if self.passes_filters(task_object, filters):
                    objects.append(task_object)

        serializer = TaskSerializer(objects, many=True, store=store)
        return Response(serializer.data)

    @requires_task_store
    @git_managed('Create task', sync=True)
    def create(self, request, store=None):
        cleaned_values = {}
        for key, value in request.data.items():
            if value is not None:
                cleaned_values[key] = value

        serializer = TaskSerializer(data=cleaned_values, store=store)
        serializer.is_valid(raise_exception=True)

        task = serializer.create(store, serializer.validated_data)
        serializer = TaskSerializer(task, store=store)
        store.log_message(
            'New task created: %s.',
            serializer.data,
        )
        return Response(serializer.data)

    @requires_task_store
    def retrieve(self, request, store=None, pk=None):
        with timed_activity(store, 'Get task by ID'):
            task = store.client.get_task(uuid=pk)[1]

        if not task:
            raise NotFound()

        serializer = TaskSerializer(task, store=store)
        return Response(serializer.data)

    @requires_task_store
    @git_managed('Update task', sync=True)
    def update(self, request, store=None, pk=None):
        cleaned_values = {}
        for key, value in request.data.items():
            if value is not None:
                cleaned_values[key] = value

        serializer = TaskSerializer(data=cleaned_values, store=store)
        serializer.is_valid(raise_exception=True)

        task, changes = serializer.update(
            store,
            pk,
            serializer.validated_data
        )
        store.log_message(
            'Task %s updated: %s.',
            pk,
            changes,
        )

        serializer = TaskSerializer(task, store=store)
        return Response(serializer.data)

    @requires_task_store
    @git_managed('Complete task', sync=True)
    def destroy(self, request, store=None, pk=None):
        try:
            store.client.task_done(uuid=pk)
            store.log_message(
                'Task %s completed.',
                pk,
            )
        except ValueError:
            raise NotFound()

        task = store.client.get_task(uuid=pk)[1]
        serializer = TaskSerializer(task, store=store)
        return Response(serializer.data)

    @requires_task_store
    @git_managed('Start task', sync=True)
    @action(detail=True, methods=['post'])
    def start(self, request, store=None, pk=None):
        store.client.task_start(uuid=pk)
        return Response()

    @requires_task_store
    @git_managed('Stop task', sync=True)
    @action(detail=True, methods=['post'])
    def stop(self, request, store=None, pk=None):
        store.client.task_stop(uuid=pk)
        return Response()

    @requires_task_store
    @git_managed('Delete task', sync=True)
    @action(detail=True, methods=['post'])
    def delete(self, request, store=None, pk=None):
        store.client.task_delete(uuid=pk)
        return Response()

    @requires_task_store
    @action(detail=False, methods=['delete', 'get'])
    def lock(self, request, store=None):
        lock_name = get_lock_name_for_store(store)
        client = get_lock_redis()

        if request.method == 'DELETE':
            value = client.delete(lock_name)
            if value:
                store.log_message('Lockfile manually deleted.')
            return Response({'status': value})
        elif request.method == 'GET':
            value = client.get(lock_name)
            if not value:
                raise NotFound()
            return Response({'status': value})

    @requires_task_store
    @action(detail=False, methods=['post'])
    def revert(self, request, store=None):
        old_head = store.repository.head().decode('utf-8')
        new_head = (
            store.repository.get_object(old_head).parents[0].decode('utf-8')
        )

        with git_checkpoint(store, "Reverting to previous commit", sync=True):
            store.git_reset(new_head.encode('utf-8'))

        store.log_message(
            "Taskstore was reverted from %s to %s via user-initiated "
            "revert operation.",
            old_head,
            new_head,
        )

        return Response({
            'old_head': old_head,
            'new_head': new_head,
        })

    @requires_task_store
    @action(detail=False, methods=['post'])
    def sync(self, request, store=None):
        result = store.sync(asynchronous=False)
        if not result:
            return Response(
                {
                    'error_message': (
                        'Synchronization is currently disabled '
                        'for your account.'
                    )
                },
                status=406
            )
        return Response()

    @requires_task_store
    @action(detail=False, methods=['post'], url_path='sync-init')
    def sync_init(self, request, store=None):
        store.client.sync(init=True)
        return Response()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[AllowAny],
    )
    def trello(self, request, store=None):
        api_key = request.GET.get('api_key', '')
        token = Token.objects.filter(key=api_key).first()

        if not token:
            raise PermissionDenied()

        return HttpResponseRedirect(
            get_authorize_url(
                request,
                api_key=api_key,
                user=token.user
            )
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='trello/callback',
        url_name="trello_callback",
        permission_classes=[AllowAny],
    )
    def trello_callback(self, request, store=None):
        api_key = request.GET.get('api_key', '')
        token = Token.objects.filter(key=api_key).first()
        store = models.TaskStore.get_for_user(token.user)

        client = get_lock_redis()
        raw_value = client.get(
            '%s.trello_auth' % token.user.username,
        )
        if not raw_value:
            raise PermissionDenied(
                'Arrived at Trello authorization URL without having '
                'initiated a Trello authorization!'
            )
        request_token = json.loads(raw_value)

        token = get_access_token(request, api_key, request_token)
        store.trello_auth_token = token[0]

        if not store.trello_board:
            board = models.TrelloObject.create(
                store=store,
                type=models.TrelloObject.BOARD,
                name='Inthe.AM Tasks',
                desc='Tasks listed on your Inthe.AM account'
            )
            for list_data in board.client.get_list(board.id):
                obj = models.TrelloObject.objects.create(
                    id=list_data.get('id'),
                    store=store,
                    type=models.TrelloObject.LIST,
                    parent=board,
                    meta=list_data
                )
                obj.subscribe()

        store.save()
        store.sync_trello()

        return HttpResponseRedirect('/tasks/')

    @requires_task_store
    @action(detail=False, methods=['post'], url_path='trello/resynchronize')
    def trello_resynchronize(self, request, store=None):
        sync_trello_tasks.apply_async(args=(store.pk, ))
        return Response(status=202)

    @requires_task_store
    @action(detail=False, methods=['post'], url_path='trello/reset')
    def trello_reset(self, request, store=None):
        reset_trello.apply_async(args=(store.pk, ))
        return Response(status=202)

    @requires_task_store
    @action(detail=False, methods=['post'])
    def deduplicate(self, request, store=None):
        store.deduplicate_tasks()
        return Response(status=202)

    @requires_task_store
    @action(detail=False, methods=['post'], url_path='deduplication-config')
    def deduplication_config(self, request, store=None):
        try:
            enabled = int(request.POST.get('enabled', 0))
        except (TypeError, ValueError):
            return Response(status=400)

        store.auto_deduplicate = enabled
        store.save()
        return Response(status=200)


def ical_feed(request, variant, secret_id):
    if variant not in ('due', 'waiting'):
        return HttpResponseNotFound()
    try:
        store = models.TaskStore.objects.get(secret_id=secret_id)
    except:
        return HttpResponseNotFound()

    if not store.ical_enabled:
        return HttpResponseNotFound()

    if variant == 'due':
        calendar_title = "Tasks Due"
        task_filter = {
            'due.any': None,
            'status': 'pending',
        }
        field = 'due'
    elif variant == 'waiting':
        calendar_title = "Tasks Waiting"
        task_filter = {
            'status': 'waiting',
        }
        field = 'wait'

    tasks = store.client.filter_tasks(task_filter)

    calendar = Calendar()
    calendar.add('version', '2.0')
    calendar.add('prodid', '-//inthe.am//ical.%s//' % variant)
    calendar.add('X-WR-CALNAME', calendar_title)

    for task in tasks:
        if field not in task:
            continue

        event = Event()
        event.add('uid', task['uuid'])
        event.add('dtstart', task[field].date())
        event.add(
            'dtend',
            task[field].date() + datetime.timedelta(days=1)
        )
        event.add(
            'dtstamp',
            task.get(
                'modified',
                task['entry']
            )
        )
        event.add('summary', task['description'])

        calendar.add_component(event)

    return HttpResponse(
        calendar.to_ical(),
        content_type='text/calendar',
    )


@csrf_exempt
def incoming_trello(request, secret_id):
    try:
        store = models.TaskStore.objects.get(secret_id=secret_id)
    except:
        return HttpResponseNotFound()

    if request.method == 'POST':
        process_trello_action.apply_async(
            args=(store.pk, json.loads(request.body.decode('utf-8')))
        )

    return HttpResponse(
        json.dumps({
            'message': 'OK',
        }),
        content_type='application/json',
    )


@csrf_exempt
def incoming_sms(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse(status=404)

    r = TwilioResponse()

    # This request is unauthenticated; we'll need to fetch the user's
    # store directly rather than looking it up via the auth cookie.
    store = models.TaskStore.get_for_user(user)

    if not store.twilio_auth_token:
        log_args = (
            "Incoming SMS for %s, but no auth token specified.",
            user,
            user,
        )
        logger.warning(*log_args)
        store.log_error(*log_args)
        return HttpResponse(status=404)
    if store.sms_whitelist:
        incoming_number = re.sub('[^0-9]', '', request.POST['From'])
        valid_numbers = [
            re.sub('[^0-9]', '', n)
            for n in store.sms_whitelist.split('\n')
        ]
        if incoming_number not in valid_numbers:
            log_args = (
                "Incoming SMS for %s, but phone number %s is not "
                "in the whitelist.",
                user,
                incoming_number,
            )
            store.log_error(*log_args)
            logger.warning(
                *log_args,
                extra={
                    'data': {
                        'incoming_number': incoming_number,
                        'whitelist': valid_numbers,
                    }
                }
            )
            return HttpResponseForbidden()
    try:
        validator = RequestValidator(store.twilio_auth_token)
        url = request.build_absolute_uri()
        signature = request.META['HTTP_X_TWILIO_SIGNATURE']
    except (AttributeError, KeyError) as e:
        log_args = (
            "Incoming SMS for %s, but error encountered while "
            "attempting to build request validator: %s.",
            user,
            e,
        )
        logger.exception(*log_args)
        store.log_error(*log_args)
        return HttpResponseForbidden()
    if not validator.validate(url, request.POST, signature):
        log_args = (
            "Incoming SMS for %s, but validator rejected message.",
            user,
        )
        logger.warning(*log_args)
        store.log_error(*log_args)
        return HttpResponseForbidden()

    with git_checkpoint(store, "Incoming SMS", sync=True):
        from_ = request.POST['From']
        body = request.POST['Body']
        task_info = body[4:]

        if not body.lower().startswith('add'):
            if store.sms_replies >= store.REPLY_ERROR:
                r.sms("Bad Request: Unknown command.")
            log_args = (
                "Incoming SMS from %s had no recognized command: '%s'." % (
                    from_,
                    body,
                ),
            )
            logger.warning(*log_args)
            store.log_error(*log_args)
        elif not task_info:
            log_args = (
                "Incoming SMS from %s had no content." % (
                    from_,
                    body,
                ),
            )
            logger.warning(*log_args)
            store.log_error(*log_args)
            if store.sms_replies >= store.REPLY_ERROR:
                r.sms("Bad Request: Empty task.")
        else:
            task_uuid = str(uuid.uuid4())
            task_args = (
                ['add'] +
                shlex_without_quotes(store.sms_arguments) +
                shlex_without_quotes(task_info)
            )
            task_args.append('uuid:%s' % task_uuid)
            result = store.client._execute_safe(*task_args)
            stdout, stderr = result
            if store.sms_replies >= store.REPLY_ALL:
                r.sms("Added.")

            log_args = (
                "Added task %s via SMS from %s; message '%s'; "
                "automatic args: '%s';"
                "response: '%s'." % (
                    task_uuid,
                    from_,
                    body,
                    store.sms_arguments,
                    stdout,
                ),
            )
            logger.info(*log_args)
            store.log_message(*log_args)

    return HttpResponse(str(r), content_type='application/xml')
