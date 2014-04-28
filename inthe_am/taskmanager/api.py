import datetime
import json
import logging
import operator
import os
import re
import shlex
import uuid

from tastypie import (
    authentication, authorization, bundle, exceptions, fields, resources
)
from twilio.twiml import Response
from twilio.util import RequestValidator
from lockfile import LockTimeout

from django.conf.urls import url
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse, HttpResponseBadRequest,
    HttpResponseNotAllowed, HttpResponseNotFound,
    HttpResponseForbidden,
)
from django.utils.timezone import now

from . import models
from . import forms
from .context_managers import git_checkpoint
from .decorators import requires_task_store, git_managed
from .task import Task


logger = logging.getLogger(__name__)


class UserAuthorization(authorization.Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(
            pk=bundle.request.user.pk
        )

    def read_detail(self, object_list, bundle):
        return bundle.obj == bundle.request.user


class TaskStoreAuthorization(authorization.Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(
            store__user=bundle.request.user
        )

    def read_detail(self, object_list, bundle):
        return bundle.obj.store.user == bundle.request.user


class UserResource(resources.ModelResource):
    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/status/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('account_status')
            ),
            url(
                r"^(?P<resource_name>%s)/my-certificate/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('my_certificate')
            ),
            url(
                r"^(?P<resource_name>%s)/my-key/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('my_key')
            ),
            url(
                r"^(?P<resource_name>%s)/taskrc/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('taskrc_extras')
            ),
            url(
                r"^(?P<resource_name>%s)/configure-taskd/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('configure_taskd')
            ),
            url(
                r"^(?P<resource_name>%s)/reset-taskd-configuration/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('reset_taskd_configuration')
            ),
            url(
                r"^(?P<resource_name>%s)/tos-accept/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('tos_accept')
            ),
            url(
                r"^(?P<resource_name>%s)/twilio-integration/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('twilio_integration')
            ),
            url(
                r"^(?P<resource_name>%s)/clear-task-data/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('clear_task_data')
            ),
            url(
                r"^(?P<resource_name>%s)/colorscheme/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('colorscheme')
            ),
            url(
                r"^(?P<resource_name>%s)/enable-sync/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('enable_sync')
            ),
            url(
                r"^(?P<resource_name>%s)/pebble-cards-config/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('configure_pebble_cards')
            ),
            url(
                r"^(?P<resource_name>%s)/feed-config/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('configure_feed')
            ),
        ]

    def _send_file(self, out, content_type=None, **kwargs):
        if content_type is None:
            content_type = 'application/octet-stream'
        if out is None or not os.path.isfile(out):
            return HttpResponseNotFound()

        with open(out, 'r') as outfile:
            response = HttpResponse(
                outfile.read(),
                content_type=content_type,
            )
            response['Content-Disposition'] = 'attachment; filename="%s"' % (
                os.path.basename(out)
            )
            return response

    @git_managed("Reset taskd configuration", gc=False)
    def reset_taskd_configuration(self, request, store=None, **kwargs):
        if request.method != 'POST':
            raise HttpResponseNotAllowed(request.method)
        store.reset_taskd_configuration()
        store.log_message("Taskd settings reset to default.")
        return HttpResponse('OK')

    @git_managed("Configuring taskd server", gc=False)
    def configure_taskd(self, request, store=None, **kwargs):
        if request.method != 'POST':
            raise HttpResponseNotAllowed(request.method)

        form = forms.TaskdConfigurationForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest(
                json.dumps(form.errors),
                content_type='application/json',
            )
        if form.cleaned_data['trust'] == 'no' and not form.cleaned_data['ca']:
            return HttpResponseBadRequest(
                json.dumps(
                    {
                        'error_message': (
                            'You must either submit a CA Certificate or '
                            'explicitly trust the taskd server.'
                        )
                    }
                ),
                content_type='application/json',
            )

        taskd_data = {
            'taskd.server': form.cleaned_data['server'],
            'taskd.credentials': form.cleaned_data['credentials'],
        }

        cert_path = os.path.join(store.local_path, 'custom.private.cert.pem')
        with open(cert_path, 'w') as out:
            taskd_data['taskd.certificate'] = cert_path
            out.write(form.cleaned_data['certificate'])

        key_path = os.path.join(store.local_path, 'custom.private.key.pem')
        with open(key_path, 'w') as out:
            taskd_data['taskd.key'] = key_path
            out.write(form.cleaned_data['key'])

        if form.cleaned_data['ca']:
            ca_path = os.path.join(store.local_path, 'custom.ca.pem')
            with open(ca_path, 'w') as out:
                taskd_data['taskd.ca'] = ca_path
                taskd_data['taskd.trust'] = 'no'
                out.write(form.cleaned_data['ca'])
        else:
            taskd_data['taskd.ca'] = ''
            taskd_data['taskd.trust'] = 'yes'

        # Write files from form to user directory
        store.log_message("Taskd settings changed.")
        store.taskrc.update(taskd_data)

        return HttpResponse('OK')

    def configure_pebble_cards(self, request, **kwargs):
        if request.method != 'POST':
            raise HttpResponseNotAllowed(request.method)

        try:
            enabled = int(request.POST.get('enabled', 0))
        except (TypeError, ValueError):
            return HttpResponseBadRequest()

        store = models.TaskStore.get_for_user(request.user)
        store.pebble_cards_enabled = True if enabled else False
        store.save()

        return HttpResponse('OK')

    def configure_feed(self, request, **kwargs):
        if request.method != 'POST':
            raise HttpResponseNotAllowed(request.method)

        try:
            enabled = int(request.POST.get('enabled', 0))
        except (TypeError, ValueError):
            return HttpResponseBadRequest()

        store = models.TaskStore.get_for_user(request.user)
        store.feed_enabled = True if enabled else False
        store.save()

        return HttpResponse('OK')

    def enable_sync(self, request, **kwargs):
        if request.method != 'POST':
            raise HttpResponseNotAllowed(request.method)

        store = models.TaskStore.get_for_user(request.user)
        store.sync_enabled = True
        store.save()

        return HttpResponse('OK')

    def colorscheme(self, request, **kwargs):
        meta = models.UserMetadata.get_for_user(request.user)
        if request.method == 'PUT':
            meta.colorscheme = request.body
            meta.save()
            return HttpResponse('OK')
        elif request.method == 'GET':
            return HttpResponse(meta.colorscheme)
        raise HttpResponseNotAllowed(request.method)

    def tos_accept(self, request, **kwargs):
        if request.method != 'POST':
            raise HttpResponseNotAllowed(request.method)

        meta = models.UserMetadata.get_for_user(request.user)
        meta.tos_version = request.POST['version']
        meta.tos_accepted = now()
        meta.save()

        return HttpResponse('OK')

    def twilio_integration(self, request, **kwargs):
        if request.method != 'POST':
            raise HttpResponseNotAllowed(request.method)

        ts = models.TaskStore.get_for_user(request.user)
        ts.twilio_auth_token = request.POST.get('twilio_auth_token', '')
        ts.sms_whitelist = request.POST.get('sms_whitelist', '')
        ts.log_message("Twilio settings changed.")
        ts.save()
        return HttpResponse('OK')

    @git_managed("Clearing task data", gc=False)
    def clear_task_data(self, request, **kwargs):
        if request.method != 'POST':
            raise HttpResponseNotAllowed(request.method)

        ts = models.TaskStore.get_for_user(request.user)

        os.rename(
            ts.taskd_data_path,
            (
                ts.taskd_data_path
                + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            )
        )

        for path in os.listdir(ts.local_path):
            if os.path.splitext(path)[1] == '.data':
                os.unlink(
                    os.path.join(
                        ts.local_path,
                        path
                    )
                )

        return HttpResponse('OK')

    def my_certificate(self, request, **kwargs):
        if request.method != 'GET':
            raise HttpResponseNotAllowed(request.method)
        ts = models.TaskStore.get_for_user(request.user)
        return self._send_file(
            ts.taskrc.get('taskd.certificate'),
            content_type='application/x-pem-file',
        )

    def my_key(self, request, **kwargs):
        if request.method != 'GET':
            raise HttpResponseNotAllowed(request.method)
        ts = models.TaskStore.get_for_user(request.user)
        return self._send_file(
            ts.taskrc.get('taskd.key'),
            content_type='application/x-pem-file',
        )

    @git_managed("Updating custom taskrc configuration", gc=False)
    def taskrc_extras(self, request, **kwargs):
        if request.method == 'GET':
            ts = models.TaskStore.get_for_user(request.user)
            return HttpResponse(
                ts.taskrc_extras,
                content_type='text/plain'
            )
        elif request.method == 'PUT':
            ts = models.TaskStore.get_for_user(request.user)
            ts.taskrc_extras = request.body.decode(
                request.encoding if request.encoding else 'utf-8'
            )
            results = ts.apply_extras()
            ts.save()
            ts.log_message("Taskrc extras saved.")
            return HttpResponse(
                json.dumps(
                    {
                        'success': results[0],
                        'failed': results[1]
                    }
                ),
                content_type='application/json',
            )
        else:
            return HttpResponseNotAllowed(request.method)

    def account_status(self, request, **kwargs):
        if request.user.is_authenticated():
            store = models.TaskStore.get_for_user(request.user)
            meta = models.UserMetadata.get_for_user(request.user)
            user_data = {
                'logged_in': True,
                'uid': request.user.pk,
                'username': request.user.username,
                'name': (
                    request.user.first_name
                    if request.user.first_name
                    else request.user.username
                ),
                'email': request.user.email,
                'configured': store.configured,
                'taskd_credentials': store.taskrc.get('taskd.credentials'),
                'taskd_server': store.taskrc.get('taskd.server'),
                'taskd_files': store.taskd_certificate_status,
                'twilio_auth_token': store.twilio_auth_token,
                'sms_whitelist': store.sms_whitelist,
                'taskrc_extras': store.taskrc_extras,
                'api_key': store.api_key.key,
                'tos_up_to_date': meta.tos_up_to_date,
                'sms_url': reverse(
                    'incoming_sms',
                    kwargs={
                        'api_name': 'v1',
                        'resource_name': 'task',
                        'username': request.user.username,
                    }
                ),
                'colorscheme': meta.colorscheme,
                'repository_head': store.repository.head(),
                'pebble_card_url': reverse(
                    'pebble_card_url',
                    kwargs={
                        'api_name': 'v1',
                        'resource_name': 'task',
                        'secret_id': store.secret_id,
                    }
                ),
                'sync_enabled': store.sync_enabled,
                'pebble_cards_enabled': store.pebble_cards_enabled,
                'feed_enabled': store.feed_enabled,
            }
        else:
            user_data = {
                'logged_in': False,
            }
        return HttpResponse(
            json.dumps(user_data),
            content_type='application/json',
        )

    class Meta:
        always_return_data = True
        queryset = User.objects.all()
        authorization = UserAuthorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = authentication.MultiAuthentication(
            authentication.ApiKeyAuthentication(),
            authentication.SessionAuthentication(),
        )


class TaskResource(resources.Resource):
    TASK_TYPE = 'pending'

    id = fields.IntegerField(attribute='id', null=True)
    uuid = fields.CharField(attribute='uuid')
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
    depends = fields.CharField(attribute='depends', null=True)
    blocks = fields.CharField(attribute='blocks', null=True)
    annotations = fields.ListField(attribute='annotations', null=True)
    tags = fields.ListField(attribute='tags', null=True)
    imask = fields.IntegerField(attribute='imask', null=True)
    udas = fields.DictField(attribute='udas', null=True)

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/autoconfigure/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('autoconfigure')
            ),
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
                r"^(?P<resource_name>%s)/pebble-card/(?P<secret_id>[\w\d_.-]+)/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('pebble_card'),
                name='pebble_card_url',
            ),
        ]

    def manage_lock(self, request, **kwargs):
        store = models.TaskStore.get_for_user(request.user)
        lockfile = os.path.join(store.local_path, '.lock')
        if request.method == 'DELETE':
            if os.path.exists(lockfile):
                os.unlink(lockfile)
                store.log_message("Lockfile deleted.")
                return HttpResponse(
                    '',
                    status=200
                )
            store.log_error(
                "Attempted to delete lockfile, but repository was not locked."
            )
            return HttpResponse(
                '',
                status=404
            )
        elif request.method == 'GET':
            if os.path.exists(lockfile):
                return HttpResponse(
                    '',
                    status=200
                )
            return HttpResponse(
                '',
                status=404
            )
        raise HttpResponseNotAllowed(request.method)

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
            status=200
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
            status=200
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
            status=200
        )

    def incoming_sms(self, request, username, **kwargs):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse(status=404)

        r = Response()
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
            logger.warning(*log_args)
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
                r.sms("Bad Request: Empty task.")
            else:
                task_uuid = str(uuid.uuid4())
                task_args = ['add'] + shlex.split(task_info)
                task_args.append('uuid:%s' % task_uuid)
                result = store.client._execute_safe(*task_args)
                stdout, stderr = result
                r.sms("Added.")

                log_args = (
                    "Added task %s from %s; message '%s'; response: '%s'." % (
                        task_uuid,
                        from_,
                        body,
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
            task = Task(task_json, store.taskrc, store=store)
            if self.passes_filters(task, filters):
                objects.append(task)

        return objects

    @requires_task_store
    def obj_get(self, bundle, store, **kwargs):
        try:
            return Task(
                store.client.get_task(uuid=kwargs['pk'])[1],
                store.taskrc,
                store=store,
            )
        except ValueError:
            raise exceptions.NotFound()

    @requires_task_store
    def obj_create(self, bundle, store, **kwargs):
        with git_checkpoint(store, "Creating Task", sync=True):
            if not bundle.data['description']:
                raise exceptions.BadRequest(
                    "You must specify a description for each task."
                )
            safe_json = Task.from_serialized(bundle.data).get_safe_json()
            bundle.obj = Task(
                store.client.task_add(**safe_json),
                store.taskrc,
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
            bundle.data.pop('id', None)
            serialized = Task.from_serialized(bundle.data).get_safe_json()
            serialized['uuid'] = kwargs['pk']
            store.client.task_update(serialized)
            store.log_message(
                "Task %s updated: %s.",
                kwargs['pk'],
                serialized
            )
            bundle.obj = Task(
                store.client.get_task(uuid=kwargs['pk'])[1],
                store.taskrc,
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
        try:
            return super(TaskResource, self).dispatch(
                request_type, request, *args, **kwargs
            )
        except LockTimeout:
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
                status=409,
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


class CompletedTaskResource(TaskResource):
    TASK_TYPE = 'completed'

    class Meta:
        always_return_data = True
        authentication = authentication.MultiAuthentication(
            authentication.SessionAuthentication(),
            authentication.ApiKeyAuthentication(),
        )
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
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


class ActivityLogResource(resources.ModelResource):
    class Meta:
        resource_name = 'activitylog'
        queryset = models.TaskStoreActivityLog.objects.order_by('-last_seen')
        authorization = TaskStoreAuthorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = authentication.MultiAuthentication(
            authentication.ApiKeyAuthentication(),
            authentication.SessionAuthentication(),
        )
        filter_fields = [
            'last_seen',
            'created',
            'error',
            'message',
            'count'
        ]
        limit = 100
        max_limit = 400
