import copy
import datetime
import json
import logging
import operator
import os
import re
import shlex

import dateutil
import pytz
from tastypie import (
    authentication, authorization, bundle, exceptions, fields, resources
)
from twilio.twiml import Response
from twilio.util import RequestValidator
from lockfile import LockTimeout

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse, HttpResponseBadRequest,
    HttpResponseNotAllowed, HttpResponseNotFound,
    HttpResponseForbidden,
)

from . import models
from . import forms
from .context_managers import git_checkpoint
from .decorators import requires_taskd_sync, git_managed


logger = logging.getLogger(__name__)


class UserAuthorization(authorization.Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(
            pk=bundle.request.user.pk
        )

    def read_detail(self, object_list, bundle):
        return bundle.obj == bundle.request.user


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
                r"^(?P<resource_name>%s)/ca-certificate/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('ca_certificate')
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
                r"^(?P<resource_name>%s)/twilio-integration/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('twilio_integration')
            )
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

    @git_managed("Reset taskd configuration")
    def reset_taskd_configuration(self, request, store=None, **kwargs):
        if request.method != 'POST':
            raise HttpResponseNotAllowed(request.method)
        store.taskrc.update({
            'taskd.certificate': os.path.join(
                store.local_path,
                store.DEFAULT_FILENAMES['certificate']
            ),
            'taskd.key': os.path.join(
                store.local_path,
                store.DEFAULT_FILENAMES['key']
            ),
            'taskd.ca': store.server_config['ca.cert'],
            'taskd.server': settings.TASKD_SERVER,
            'taskd.credentials': store.metadata['generated_taskd_credentials']
        })
        return HttpResponse('OK')

    @git_managed("Configuring taskd server")
    def configure_taskd(self, request, store=None, **kwargs):
        if request.method != 'POST':
            raise HttpResponseNotAllowed(request.method)

        form = forms.TaskdConfigurationForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest(
                json.dumps(form.errors),
                content_type='application/json',
            )

        cert_path = os.path.join(store.local_path, 'custom.private.cert.pem')
        with open(cert_path, 'w') as out:
            out.write(form.cleaned_data['certificate'])

        key_path = os.path.join(store.local_path, 'custom.private.key.pem')
        with open(key_path, 'w') as out:
            out.write(form.cleaned_data['key'])

        ca_path = os.path.join(store.local_path, 'custom.ca.pem')
        with open(ca_path, 'w') as out:
            out.write(form.cleaned_data['ca'])

        # Write files from form to user directory
        store.taskrc.update({
            'taskd.certificate': cert_path,
            'taskd.key': key_path,
            'taskd.ca': ca_path,
            'taskd.server': form.cleaned_data['server'],
            'taskd.credentials': form.cleaned_data['credentials'],
        })

        return HttpResponse('OK')

    def twilio_integration(self, request, **kwargs):
        ts = models.TaskStore.get_for_user(request.user)
        ts.twilio_auth_token = request.POST.get('twilio_auth_token', '')
        ts.sms_whitelist = request.POST.get('sms_whitelist', '')
        ts.save()
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

    def ca_certificate(self, request, **kwargs):
        if request.method != 'GET':
            raise HttpResponseNotAllowed(request.method)
        ts = models.TaskStore.get_for_user(request.user)
        return self._send_file(
            ts.taskrc.get('taskd.ca'),
            content_type='application/x-pem-file',
        )

    @git_managed("Updating custom taskrc configuration")
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
                'taskd_is_custom': (
                    store.taskrc.get('taskd.server') != settings.TASKD_SERVER
                ),
                'twilio_auth_token': store.twilio_auth_token,
                'sms_whitelist': store.sms_whitelist,
                'taskrc_extras': store.taskrc_extras,
                'api_key': store.api_key.key,
                'sms_url': reverse(
                    'incoming_sms',
                    kwargs={
                        'api_name': 'v1',
                        'resource_name': 'task',
                        'username': request.user.username,
                    }
                )
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


class Task(object):
    DATE_FIELDS = [
        'due', 'entry', 'modified', 'start', 'wait', 'scheduled',
    ]
    LIST_FIELDS = [
        'annotations', 'tags',
    ]
    READ_ONLY_FIELDS = [
        'id', 'uuid', 'urgency', 'entry', 'modified', 'imask',
        'resource_uri', 'start',
    ]

    def __init__(self, json):
        if not json:
            raise ValueError()
        self.json = json

    @staticmethod
    def get_timezone(tzname, offset):
        if tzname is not None:
            return pytz.timezone(tzname)
        static_timezone = pytz.tzinfo.StaticTzInfo()
        static_timezone._utcoffset = datetime.timedelta(
            seconds=offset
        )
        return static_timezone

    def get_json(self):
        return self.json

    def get_safe_json(self):
        return {
            k: v for k, v in self.json.items()
            if k not in self.READ_ONLY_FIELDS
        }

    @classmethod
    def from_serialized(cls, data):
        data = copy.deepcopy(data)
        for key in data:
            if key in cls.DATE_FIELDS and data[key]:
                data[key] = dateutil.parser.parse(
                    data[key],
                    tzinfos=cls.get_timezone
                )
            elif key in cls.LIST_FIELDS and data[key] is None:
                data[key] = []
        return Task(data)

    def _date_from_taskw(self, value):
        value = datetime.datetime.strptime(
            value,
            '%Y%m%dT%H%M%SZ',
        )
        return value.replace(tzinfo=pytz.UTC)

    def _date_to_taskw(self, value):
        raise NotImplementedError()

    def __getattr__(self, name):
        try:
            value = self.json[name]
            if name in self.DATE_FIELDS:
                value = self._date_from_taskw(value)
            elif name == 'annotations':
                new_value = []
                for annotation in value:
                    annotation['entry'] = self._date_from_taskw(
                        annotation['entry']
                    )
                    new_value.append(annotation)
                value = new_value
            return value
        except KeyError:
            raise AttributeError()

    @property
    def id(self):
        return self.json['id'] if self.json['id'] else None

    @property
    def urgency(self):
        return float(self.json['urgency']) if self.json['urgency'] else None

    def __unicode__(self):
        return self.description


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
    annotations = fields.ListField(attribute='annotations', null=True)
    tags = fields.ListField(attribute='tags', null=True)
    imask = fields.IntegerField(attribute='imask', null=True)

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
        ]

    def manage_lock(self, request, **kwargs):
        store = models.TaskStore.get_for_user(request.user)
        lockfile = os.path.join(store.local_path, '.lock')
        if request.method == 'DELETE':
            if os.path.exists(lockfile):
                os.unlink(lockfile)
                return HttpResponse(
                    '',
                    status=200
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

    @requires_taskd_sync
    @git_managed("Start task")
    def start_task(self, request, uuid, store, **kwargs):
        if not request.method == 'POST':
            return HttpResponseNotAllowed(request.method)
        store.client.task_start(uuid=uuid)
        return HttpResponse(
            status=200
        )

    @requires_taskd_sync
    @git_managed("Stop task")
    def stop_task(self, request, uuid, store, **kwargs):
        if not request.method == 'POST':
            return HttpResponseNotAllowed(request.method)
        store.client.task_stop(uuid=uuid)
        return HttpResponse(
            status=200
        )

    @requires_taskd_sync
    @git_managed("Delete task")
    def delete(self, request, uuid, store, **kwargs):
        if not request.method == 'POST':
            return HttpResponseNotAllowed(request.method)
        store.client.task_delete(uuid=uuid)
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
            logger.warning(
                "Incoming SMS for %s, but no auth token specified.",
                user,
                user,
            )
            return HttpResponse(status=404)
        if store.sms_whitelist:
            incoming_number = re.sub('[^0-9]', '', request.POST['From'])
            valid_numbers = [
                re.sub('[^0-9]', '', n)
                for n in store.sms_whitelist.split('\n')
            ]
            if incoming_number not in valid_numbers:
                logger.warning(
                    "Incoming SMS for %s, but phone number %s is not "
                    "in the whitelist.",
                    user,
                    incoming_number,
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
            logger.warning(
                "Incoming SMS for %s, but error encountered while "
                "attempting to build request validator: %s.",
                user,
                e,
            )
            return HttpResponseForbidden()
        if not validator.validate(url, request.POST, signature):
            logger.warning(
                "Incoming SMS for %s, but validator rejected message.",
                user,
            )
            return HttpResponseForbidden()

        with git_checkpoint(store, "Incoming SMS", sync=True):
            from_ = request.POST['From']
            body = request.POST['Body']
            task_info = body[4:]

            if not body.lower().startswith('add'):
                r.sms("Bad Request: Unknown command.")
                logger.warning(
                    "Incoming SMS from %s had no recognized command: '%s'" % (
                        from_,
                        body,
                    )
                )
            elif not task_info:
                logger.warning(
                    "Incoming SMS from %s had no content." % (
                        from_,
                        body,
                    )
                )
                r.sms("Bad Request: Empty task.")
            else:
                task_args = ['add'] + shlex.split(task_info)
                result = store.client._execute_safe(*task_args)
                stdout, stderr = result
                r.sms("Added.")

                logger.info(
                    "Added task from %s; message '%s'; response: '%s'" % (
                        from_,
                        body,
                        stdout,
                    )
                )

        return HttpResponse(str(r), content_type='application/xml')

    def autoconfigure(self, request, **kwargs):
        store = models.TaskStore.get_for_user(request.user)
        try:
            store.autoconfigure_taskd()
        except Exception as e:
            return HttpResponse(
                json.dumps({
                    'error': str(e)
                }),
                status=500,
                content_type='application/json',
            )
        return HttpResponse(
            json.dumps({
                'status': 'Successfully configured'
            }),
            status=200,
            content_type='application/json',
        )

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

    @requires_taskd_sync
    def obj_get_list(self, bundle, store, **kwargs):
        if hasattr(bundle.request, 'GET'):
            filters = bundle.request.GET.copy()
        filters.update(kwargs)

        objects = []
        for task_json in store.client.load_tasks()[self.TASK_TYPE]:
            task = Task(task_json)
            if self.passes_filters(task, filters):
                objects.append(task)

        return objects

    @requires_taskd_sync
    def obj_get(self, bundle, store, **kwargs):
        try:
            return Task(store.client.get_task(uuid=kwargs['pk'])[1])
        except ValueError:
            raise exceptions.NotFound()

    @requires_taskd_sync
    def obj_create(self, bundle, store, **kwargs):
        with git_checkpoint(store, "Creating Task"):
            bundle.obj = Task(
                store.client.task_add(
                    **Task.from_serialized(bundle.data).get_safe_json()
                )
            )
            return bundle

    @requires_taskd_sync
    def obj_update(self, bundle, store, **kwargs):
        with git_checkpoint(store, "Updating Task"):
            if bundle.data['uuid'] != kwargs['pk']:
                raise exceptions.BadRequest(
                    "Changing the UUID of an existing task is not possible."
                )
            bundle.data.pop('id', None)
            serialized = Task.from_serialized(bundle.data).get_safe_json()
            serialized['uuid'] = kwargs['pk']
            store.client.task_update(serialized)
            bundle.obj = Task(store.client.get_task(uuid=kwargs['pk'])[1])
            return bundle

    def obj_delete_list(self, bundle, store, **kwargs):
        raise exceptions.BadRequest()

    def dispatch(self, *args, **kwargs):
        try:
            return super(TaskResource, self).dispatch(*args, **kwargs)
        except LockTimeout:
            return HttpResponse(
                json.dumps(
                    {
                        'error_message': (
                            'Your task list is currently locked by another client.'
                            'If this error persists, you may try ',
                            'clearing the lockfile by sending a DELETE request '
                            'to http://inthe.am/api/v1/task/lock/. '
                            'Please refer to the API documentation for details.'
                        )
                    }
                ),
                status=409,
            )

    @requires_taskd_sync
    def obj_delete(self, bundle, store, **kwargs):
        with git_checkpoint(store, "Completing Task"):
            try:
                store.client.task_done(uuid=kwargs['pk'])
                return bundle
            except ValueError:
                raise exceptions.NotFound()

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
