import datetime
import json
import logging
import operator
import os
import shlex

import pytz
from tastypie import (
    authentication, authorization, bundle, exceptions, fields, resources
)
from twilio.twiml import Response

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse, HttpResponseBadRequest,
    HttpResponseNotAllowed, HttpResponseNotFound
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

    @git_managed("Configuring taskd server")
    def configure_taskd(self, request, store=None, **kwargs):
        if request.method != 'POST':
            raise HttpResponseNotAllowed(
                'Only POST requests are allowed'
            )

        form = forms.TaskdConfigurationForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest(
                json.dumps(form.errors),
                content_type='application/json',
            )

        cert_path = os.path.join(store.local_path, 'private.cert.pem')
        with open(cert_path, 'w') as out:
            out.write(form.cleaned_data['certificate'])

        key_path = os.path.join(store.local_path, 'private.key.pem')
        with open(key_path, 'w') as out:
            out.write(form.cleaned_data['key'])

        ca_path = os.path.join(store.local_path, 'ca.pem')
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

    def my_certificate(self, request, **kwargs):
        if request.method != 'GET':
            raise HttpResponseNotAllowed(
                'Only GET requests are allowed'
            )
        ts = models.TaskStore.get_for_user(request.user)
        return self._send_file(
            ts.certificate_path,
            content_type='application/x-pem-file',
        )

    def my_key(self, request, **kwargs):
        if request.method != 'GET':
            raise HttpResponseNotAllowed(
                'Only GET requests are allowed'
            )
        ts = models.TaskStore.get_for_user(request.user)
        return self._send_file(
            ts.key_path,
            content_type='application/x-pem-file',
        )

    def ca_certificate(self, request, **kwargs):
        if request.method != 'GET':
            raise HttpResponseNotAllowed(
                'Only GET requests are allowed'
            )
        ts = models.TaskStore.get_for_user(request.user)
        return self._send_file(
            ts.server_config.get('ca.cert'),
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
            ts.taskrc_extras = request.body.decode(request.encoding)
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
            return HttpResponseNotAllowed(
                'Only GET or PUT requests are allowed'
            )

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
                'taskrc_extras': store.taskrc_extras,
                'api_key': request.user.api_key.key,
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

    def __init__(self, json):
        if not json:
            raise ValueError()
        self.json = json

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
                r"^(?P<resource_name>%s)/(?P<uuid>[\w\d_.-]+)/complete/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('complete')
            ),
            url(
                r"^(?P<resource_name>%s)/(?P<uuid>[\w\d_.-]+)/delete/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('delete')
            ),
        ]

    @git_managed("Mark task completed")
    @requires_taskd_sync
    def complete(self, request, uuid, store, **kwargs):
        store.client.task_done(uuid=uuid)
        return HttpResponse(
            status=200
        )

    @git_managed("Delete task")
    def delete(self, request, uuid, **kwargs):
        return HttpResponse(
            status=501
        )

    def incoming_sms(self, request, username, **kwargs):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse(status=404)

        r = Response()
        store = models.TaskStore.get_for_user(user)

        with git_checkpoint(store, "Incoming SMS"):
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
                store.sync()
                task_args = ['add'] + shlex.split(task_info)
                result = store.client._execute(*task_args)
                stdout, stderr = result
                r.sms("Added.")

                logger.info(
                    "Added task from %s; message '%s'; response: '%s'" % (
                        from_,
                        body,
                        stdout,
                    )
                )

                store.sync()
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
        for key, value in filters.items():
            task_value = getattr(task, key, None)
            if task_value == value:
                return True
        return False

    @requires_taskd_sync
    def obj_get_list(self, bundle, store, **kwargs):
        if hasattr(bundle.request, 'GET'):
            filters = bundle.request.GET.copy()
        filters.update(kwargs)

        key = 'pending'
        if int(bundle.request.GET.get('completed', 0)):
            key = 'completed'

        objects = []
        for task_json in store.client.load_tasks()[key]:
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

    class Meta:
        authentication = authentication.MultiAuthentication(
            authentication.ApiKeyAuthentication(),
            authentication.SessionAuthentication(),
        )
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        limit = 1000
        max_limit = 1000
