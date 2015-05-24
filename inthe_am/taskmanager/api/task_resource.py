import json
import logging
import re
import operator
import shlex
import uuid

from dateutil.parser import parse
from taskw.fields import DateField
from taskw.task import Task as TaskwTask
from tastypie import (
    authentication,
    authorization,
    bundle,
    exceptions,
    fields,
    resources,
)
from tastypie.bundle import Bundle
from twilio.twiml import Response
from twilio.util import RequestValidator

from django.conf.urls import url
from django.contrib.auth.models import User
from django.http import (
    HttpResponse, HttpResponseBadRequest,
    HttpResponseNotAllowed, HttpResponseNotFound,
    HttpResponseForbidden,
)

from .. import models
from ..api_fields import UUIDField
from ..context_managers import git_checkpoint
from ..lock import get_lock_name_for_store, get_lock_redis
from ..decorators import (
    git_managed,
    process_authentication,
    requires_task_store
)
from ..task import Task
from .mixins import LockTimeoutMixin


logger = logging.getLogger(__name__)


class TaskResource(LockTimeoutMixin, resources.Resource):
    TASK_TYPE = 'pending'
    SYNTHETIC_FIELDS = [
        'blocks',
    ]

    id = UUIDField(attribute='uuid', null=True)
    uuid = UUIDField(attribute='uuid')
    short_id = fields.IntegerField(attribute='id', null=True)
    status = fields.CharField(attribute='status')
    urgency = fields.FloatField(attribute='urgency')
    description = fields.CharField(attribute='description')
    priority = fields.CharField(attribute='priority', null=True)
    project = fields.CharField(attribute='project', null=True)
    due = fields.DateTimeField(attribute='due', null=True)
    entry = fields.DateTimeField(attribute='entry', null=True)
    modified = fields.DateTimeField(attribute='modified', null=True)
    start = fields.DateTimeField(attribute='start', null=True)
    wait = fields.DateTimeField(attribute='wait', null=True)
    scheduled = fields.DateTimeField(attribute='scheduled', null=True)
    depends = fields.ListField(attribute='depends', null=True)
    blocks = fields.ListField(attribute='blocks', null=True)
    annotations = fields.ListField(attribute='annotations', null=True)
    tags = fields.ListField(attribute='tags', null=True)
    imask = fields.IntegerField(attribute='imask', null=True)

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/(?P<username>[\w\d_.-]+)/sms/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('incoming_sms'),
                name="incoming_sms"
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<uuid>[\w\d_.-]+)/start/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('start_task')
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<uuid>[\w\d_.-]+)/stop/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('stop_task')
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<uuid>[\w\d_.-]+)/delete/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('delete')
            ),
            url(
                r"^(?P<resource_name>%s)/lock/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('manage_lock')
            ),
            url(
                r"^(?P<resource_name>%s)/pebble-card/"
                r"(?P<secret_id>[\w\d_.-]+)/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('pebble_card'),
                name='pebble_card_url',
            ),
            url(
                r"^(?P<resource_name>%s)/refresh/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('refresh_tasks'),
                name='refresh_tasks',
            ),
            url(
                r"^(?P<resource_name>%s)/revert/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('revert_to_last_commit'),
                name='revert_to_last_commit',
            ),
            url(
                r"^(?P<resource_name>%s)/sync/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('sync_immediately'),
                name='sync_immediately',
            ),
            url(
                r"^(?P<resource_name>%s)/sync-init/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('sync_init'),
                name='sync_init',
            )
        ]

    def get_task_store(self, request):
        return models.TaskStore.get_for_user(request.user)

    def dehydrate(self, bundle):
        store = self.get_task_store(bundle.request)
        for key, data in store.client.config.get_udas().items():
            value = getattr(bundle.obj, key.encode('utf8'), None)
            bundle.data[key] = value
        return bundle

    def hydrate(self, bundle):
        store = self.get_task_store(bundle.request)
        for key, field_instance in store.client.config.get_udas().items():
            value = bundle.data.get(key, None)
            if value and isinstance(field_instance, DateField):
                try:
                    setattr(bundle.obj, key, parse(value))
                except (TypeError, ValueError):
                    raise exceptions.BadRequest(
                        "Invalid date provided for field %s: " % (
                            key,
                            value,
                        )
                    )
            elif value:
                setattr(bundle.obj, key, value)

        try:
            depends = []
            for task_id in bundle.data.get('depends', []):
                depends.append(uuid.UUID(task_id))
            bundle.data['depends'] = depends
        except (TypeError, ValueError):
            raise exceptions.BadRequest(
                "Invalid task IDs provided for field depends: %s" % (
                    bundle.data.get('depends')
                )
            )

        return bundle

    @process_authentication()
    def manage_lock(self, request, **kwargs):
        store = self.get_task_store(request)
        lock_name = get_lock_name_for_store(store)
        client = get_lock_redis()

        if request.method == 'DELETE':
            value = client.delete(lock_name)
            if value:
                store.log_message("Lockfile deleted.")
                return HttpResponse(
                    json.dumps({
                        'lock_status': value,
                    }),
                    status=200
                )
            store.log_error(
                "Attempted to delete lockfile, but repository was not locked."
            )
            return HttpResponse(
                json.dumps({
                    'error_message': 'Repository is not locked'
                }),
                status=404
            )
        elif request.method == 'GET':
            value = client.get(lock_name)
            if value:
                return HttpResponse(
                    json.dumps({
                        'lock_status': value,
                    }),
                    status=200
                )
            return HttpResponse(
                json.dumps({
                    'error_message': 'Repository is not locked'
                }),
                status=404
            )
        return HttpResponseNotAllowed(request.method)

    @requires_task_store
    def revert_to_last_commit(self, request, store, **kwargs):
        if request.method != 'POST':
            return HttpResponseBadRequest(request.method)

        old_head = store.repository.head()
        new_head = store.repository.get_object(old_head).parents[0]

        with git_checkpoint(store, "Reverting to previous commit", sync=True):
            store.git_reset(new_head)

        store.log_message(
            "Taskstore was reverted from %s to %s via user-initiated "
            "revert operation.",
            old_head,
            new_head,
        )

        return HttpResponse(
            json.dumps({
                'message': 'OK',
                'old_head': old_head,
                'new_head': new_head
            }),
            content_type='application/json',
        )

    @requires_task_store
    def sync_immediately(self, request, store, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)

        result = store.sync(async=False)
        if not result:
            return HttpResponse(
                json.dumps({
                    'error_message': (
                        'Synchronization is currently disabled '
                        'for your account.'
                    )
                }),
                content_type='application/json',
                status=406,
            )
        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @requires_task_store
    @git_managed("Sync init", sync=False)
    def sync_init(self, request, store, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)

        store.client.sync(init=True)
        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @requires_task_store
    def refresh_tasks(self, request, store, **kwargs):
        """ Refreshes the task list manually.

        .. warning::

           This method is DEPRECATED, and will be removed
           in a future version.

        """
        if request.method != 'GET':
            return HttpResponseNotAllowed(request.method)
        try:
            head = request.GET['head']
        except KeyError:
            return HttpResponseBadRequest()

        store.sync(async=False)

        changes = []

        new_head = store.repository.head()
        for id in store.get_changed_task_ids(head, new_head):
            changes.append(
                {
                    'action': 'task_changed',
                    'body': id,
                }
            )

        if new_head != head:
            changes.append(
                {
                    'action': 'head_changed',
                    'body': new_head
                }
            )

        response = {
            'messages': changes,
        }

        return HttpResponse(
            json.dumps(response),
            content_type='application/json',
        )

    def pebble_card(self, request, secret_id, **kwargs):
        if request.method != 'GET':
            return HttpResponseNotAllowed(request.method)
        try:
            store = models.TaskStore.objects.get(secret_id=secret_id)
        except:
            return HttpResponseNotFound()

        if not store.pebble_cards_enabled:
            return HttpResponseNotFound()

        pending_tasks = store.client.filter_tasks({'status': self.TASK_TYPE})
        pending_tasks = sorted(
            pending_tasks,
            key=lambda d: float(d['urgency']),
            reverse=True
        )

        response = {
            'content': None,
            'refresh_frequency': 15
        }
        try:
            response['content'] = pending_tasks[0]['description']
        except IndexError:
            response['content'] = 'No tasks exist'

        return HttpResponse(
            json.dumps(response),
            content_type='application/json',
        )

    @requires_task_store
    @git_managed("Start task", sync=True)
    def start_task(self, request, uuid, store, **kwargs):
        if not request.method == 'POST':
            return HttpResponseNotAllowed(request.method)
        try:
            store.client.task_start(uuid=uuid)
        except ValueError:
            raise exceptions.NotFound()
        store.log_message("Task %s started.", uuid)
        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @requires_task_store
    @git_managed("Stop task", sync=True)
    def stop_task(self, request, uuid, store, **kwargs):
        if not request.method == 'POST':
            return HttpResponseNotAllowed(request.method)
        try:
            store.client.task_stop(uuid=uuid)
        except ValueError:
            raise exceptions.NotFound()
        store.log_message("Task %s stopped.", uuid)
        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @requires_task_store
    @git_managed("Delete task", sync=True)
    def delete(self, request, uuid, store, **kwargs):
        if not request.method == 'POST':
            return HttpResponseNotAllowed(request.method)
        try:
            store.client.task_delete(uuid=uuid)
        except ValueError:
            raise exceptions.NotFound()

        store.log_message("Task %s deleted.", uuid)
        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    def incoming_sms(self, request, username, **kwargs):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse(status=404)

        r = Response()

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
                    shlex.split(store.sms_arguments) +
                    shlex.split(task_info)
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

    def _get_store(self, user):
        return user.task_stores.get()

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, bundle.Bundle):
            kwargs['pk'] = bundle_or_obj.obj.uuid
        else:
            kwargs['pk'] = bundle_or_obj.uuid

        return kwargs

    def apply_sorting(self, obj_list, options=None):
        if options is None:
            options = {}

        parameter_name = 'order_by'

        if hasattr(options, 'getlist'):
            order_bits = options.getlist(parameter_name)
        else:
            order_bits = options.get(parameter_name)

            if not isinstance(order_bits, list, tuple):
                order_bits = [order_bits]

        if not order_bits:
            order_bits = ['-urgency']

        order_by_args = []
        for order_by in order_bits:
            order_by_bits = order_by.split(',')

            field_name = order_by_bits[0]
            reverse = False

            if order_by_bits[0].startswith('-'):
                field_name = order_by_bits[0][1:]
                reverse = True

            order_by_args.append(
                (field_name, reverse)
            )

        order_by_args.reverse()
        for arg, reverse in order_by_args:
            obj_list = sorted(
                obj_list,
                key=operator.attrgetter(arg),
                reverse=reverse,
            )

        return obj_list

    def passes_filters(self, task, filters):
        passes = True
        for key, value in filters.items():
            if key not in self.Meta.filter_fields:
                continue
            task_value = getattr(task, key, None)
            if task_value != value:
                passes = False
        return passes

    @requires_task_store
    def obj_get_list(self, bundle, store, **kwargs):
        if hasattr(bundle.request, 'GET'):
            filters = bundle.request.GET.copy()
        filters.update(kwargs)

        objects = []
        for task_json in store.client.filter_tasks({'status': self.TASK_TYPE}):
            task = Task(task_json, store=store)
            if self.passes_filters(task, filters):
                objects.append(task)

        return objects

    @requires_task_store
    def obj_get(self, bundle, store, **kwargs):
        task = store.client.get_task(uuid=kwargs['pk'])[1]
        if not task:
            repository_head = store.repository.head()
            logger.warning(
                'Unable to find task with ID %s in repository %s at %s',
                kwargs['pk'],
                store.local_path,
                repository_head,
                extra={
                    'data': {
                        'store': store,
                        'local_path': store.local_path,
                        'pk': kwargs['pk'],
                        'head': repository_head
                    }
                }
            )
            raise exceptions.NotFound()
        return Task(task, store=store)

    @requires_task_store
    def obj_create(self, bundle, store, **kwargs):
        with git_checkpoint(store, "Creating Task", sync=True):
            if not bundle.data['description']:
                raise exceptions.BadRequest(
                    "You must specify a description for each task."
                )

            bundle.obj = self.get_empty_task(bundle.request)
            bundle = self.full_hydrate(bundle)
            data = bundle.obj.get_json()

            for k in self.SYNTHETIC_FIELDS:
                if k in data:
                    data.pop(k, None)
            for k, v in TaskwTask.FIELDS.items():
                if k in data and v.read_only:
                    data.pop(k, None)
            for k, v in data.items():
                if not v:
                    data.pop(k)

            bundle.obj = Task(
                store.client.task_add(**data),
                store=store,
            )
            store.log_message(
                "New task created: %s.",
                bundle.obj.get_json(),
            )
            return bundle

    @requires_task_store
    def obj_update(self, bundle, store, **kwargs):
        with git_checkpoint(store, "Updating Task", sync=True):
            if bundle.data['uuid'] != kwargs['pk']:
                raise exceptions.BadRequest(
                    "Changing the UUID of an existing task is not possible."
                )
            elif not bundle.data['description']:
                raise exceptions.BadRequest(
                    "You must specify a description for each task."
                )
            original = store.client.get_task(uuid=kwargs['pk'])[1]
            if not original:
                raise exceptions.NotFound()

            bundle.obj = self.get_empty_task(bundle.request)

            bundle = self.full_hydrate(bundle)

            data = bundle.obj.get_json()
            for k in json.loads(bundle.request.body).keys():
                v = data.get(k)
                if (
                    (
                        k in original.FIELDS
                        and original.FIELDS[k].read_only
                    ) or k in self.SYNTHETIC_FIELDS
                ):
                    continue
                original[k] = v

            changes = original.get_changes(keep=True)

            store.client.task_update(original)
            store.log_message(
                "Task %s updated: %s.",
                kwargs['pk'],
                changes,
            )
            bundle.obj = Task(
                store.client.get_task(uuid=kwargs['pk'])[1],
                store=store,
            )
            return bundle

    @requires_task_store
    def obj_delete(self, bundle, store, **kwargs):
        with git_checkpoint(store, "Completing Task", sync=True):
            try:
                store.log_message("Task %s completed.", kwargs['pk'])
                store.client.task_done(uuid=kwargs['pk'])
                return bundle
            except ValueError:
                raise exceptions.NotFound()

    def obj_delete_list(self, bundle, store, **kwargs):
        raise exceptions.BadRequest()

    def dispatch(self, request_type, request, *args, **kwargs):
        if request.user.is_authenticated():
            metadata = models.UserMetadata.get_for_user(request.user)
        else:
            metadata = None
        if metadata and not metadata.tos_up_to_date:
            return HttpResponse(
                json.dumps(
                    {
                        'error_message': (
                            'Please accept the terms of service at '
                            'https://inthe.am/terms-of-use.'
                        )
                    }
                ),
                status=403
            )
        return super(TaskResource, self).dispatch(
            request_type, request, *args, **kwargs
        )

    def get_empty_task(self, request):
        store = self.get_task_store(request)
        return self._meta.object_class(store=store)

    def build_bundle(
        self, obj=None, data=None, request=None, objects_saved=None
    ):
        """ Builds the bundle!

        Overridden only to properly build the `Task` entry with its object.

        """
        if obj is None and self._meta.object_class:
            obj = self.get_empty_task(request)

        return Bundle(
            obj=obj,
            data=data,
            request=request,
            objects_saved=objects_saved
        )

    class Meta:
        always_return_data = True
        authorization = authorization.Authorization()
        authentication = authentication.MultiAuthentication(
            authentication.SessionAuthentication(),
            authentication.ApiKeyAuthentication(),
        )
        list_allowed_methods = ['get', 'put', 'post', 'delete']
        detail_allowed_methods = ['get', 'put', 'post', 'delete']
        filter_fields = [
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
        limit = 100
        max_limit = 400
        object_class = Task
