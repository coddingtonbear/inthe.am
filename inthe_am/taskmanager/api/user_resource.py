import datetime
import json
import logging
import os
import textwrap

from tastypie import (
    authentication,
    resources
)

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse, HttpResponseBadRequest,
    HttpResponseNotAllowed, HttpResponseNotFound,
    HttpResponseForbidden,
)
from django.template.loader import render_to_string
from django.utils.timezone import now

from ..decorators import (
    git_managed,
    process_authentication,
)
from .. import forms
from .. import models
from .authorizations import UserAuthorization
from .mixins import LockTimeoutMixin


logger = logging.getLogger(__name__)


def get_published_properties(user, store, meta):
    return {
        'logged_in': True,
        'uid': user.pk,
        'username': user.username,
        'name': (
            user.first_name
            if user.first_name
            else user.username
        ),
        'email': user.email,
        'configured': store.configured,
        'taskd_credentials': store.taskrc.get('taskd.credentials'),
        'taskd_server': store.taskrc.get('taskd.server'),
        'taskd_server_is_default': store.sync_uses_default_server,
        'streaming_enabled': (
            settings.STREAMING_UPDATES_ENABLED and
            store.sync_uses_default_server
        ),
        'taskd_files': store.taskd_certificate_status,
        'twilio_auth_token': store.twilio_auth_token,
        'sms_whitelist': store.sms_whitelist,
        'sms_arguments': store.sms_arguments,
        'sms_replies': store.sms_replies,
        'email_whitelist': store.email_whitelist,
        'task_creation_email_address': '%s@inthe.am' % (
            store.secret_id
        ),
        'taskrc_extras': store.taskrc_extras,
        'api_key': store.api_key.key,
        'tos_up_to_date': meta.tos_up_to_date,
        'feed_url': reverse(
            'feed',
            kwargs={
                'uuid': store.secret_id,
            }
        ),
        'sms_url': reverse(
            'incoming_sms',
            kwargs={
                'api_name': 'v1',
                'resource_name': 'task',
                'username': user.username,
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
        'kanban_memberships': [
            (s.kanban_board.name, reverse(
                'kanban_members_detail',
                kwargs={
                    'uuid': s.kanban_board.uuid,
                    'member_uuid': s.uuid,
                },
            ), )
            for s in store.get_kanban_memberships()
        ],
        'sync_enabled': store.sync_enabled,
        'pebble_cards_enabled': store.pebble_cards_enabled,
        'feed_enabled': store.feed_enabled,
        'udas': [
            {
                'field': k,
                'label': v.label,
                'type': v.__class__.__name__
            } for k, v in store.client.config.get_udas().items()
        ]
    }


class UserResource(LockTimeoutMixin, resources.ModelResource):
    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/status/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('account_status')
            ),
            url(
                r"^(?P<resource_name>%s)/announcements/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('announcements')
            ),
            url(
                r"^(?P<resource_name>%s)/generate-new-certificate/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('generate_new_certificate')
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
                r"^(?P<resource_name>%s)/email-integration/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('email_integration')
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
            url(
                r"^(?P<resource_name>%s)/mirakel-configuration/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('mirakel_configuration')
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

    @git_managed("Reset taskd configuration", gc=False)
    @process_authentication()
    def reset_taskd_configuration(self, request, store=None, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)
        store.reset_taskd_configuration()
        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @git_managed("Configuring taskd server", gc=False)
    @process_authentication()
    def configure_taskd(self, request, store=None, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)
        if store.sync_uses_default_server:
            return HttpResponse(
                json.dumps({
                    'error_message': (
                        'This functionality is no longer available. '
                        'See https://github.com/coddingtonbear/'
                        'inthe.am/issues/167 for more information.'
                    ),
                }),
                status=410,
                content_type='application/json',
            )

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

        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @process_authentication()
    def configure_pebble_cards(self, request, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)

        try:
            enabled = int(request.POST.get('enabled', 0))
        except (TypeError, ValueError):
            return HttpResponseBadRequest()

        store = models.TaskStore.get_for_user(request.user)
        store.pebble_cards_enabled = True if enabled else False
        store.save()

        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @process_authentication()
    def configure_feed(self, request, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)

        try:
            enabled = int(request.POST.get('enabled', 0))
        except (TypeError, ValueError):
            return HttpResponseBadRequest()

        store = models.TaskStore.get_for_user(request.user)
        store.feed_enabled = True if enabled else False
        store.save()

        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @process_authentication()
    def mirakel_configuration(self, request, **kwargs):
        if request.method != 'GET':
            raise HttpResponseBadRequest()

        store = models.TaskStore.get_for_user(request.user)

        with open(store.taskrc['taskd.certificate'], 'r') as fin:
            client_cert = fin.read().strip()
        with open(store.taskrc['taskd.key'], 'r') as fin:
            client_key = fin.read().strip()
        with open(store.taskrc['taskd.ca'], 'r') as fin:
            ca_cert = fin.read().strip()

        org, username, user_key = store.taskrc['taskd.credentials'].split('/')
        response = HttpResponse(
            render_to_string(
                'mirakel_configuration.txt',
                {
                    'username': username,
                    'org': org,
                    'user_key': user_key,
                    'taskd_server': store.taskrc['taskd.server'],
                    'client_cert': client_cert,
                    'client_key': client_key,
                    'ca_cert': ca_cert,
                }
            ),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = 'attachment; filename="%s"' % (
            "%s.taskdconfig" % store.username
        )
        return response

    @process_authentication()
    def enable_sync(self, request, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)

        store = models.TaskStore.get_for_user(request.user)
        if not store.sync_permitted:
            return HttpResponseForbidden(
                "Synchronization cannot be enabled for your account; "
                "please contact admin@inthe.am for more information."
            )
        store.sync_enabled = True
        store.save()

        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @process_authentication()
    def colorscheme(self, request, **kwargs):
        meta = models.UserMetadata.get_for_user(request.user)
        if request.method == 'PUT':
            meta.colorscheme = request.body
            meta.save()
            return HttpResponse(
                json.dumps({
                    'message': 'OK',
                }),
                content_type='application/json',
            )
        elif request.method == 'GET':
            return HttpResponse(meta.colorscheme)
        return HttpResponseNotAllowed(request.method)

    def tos_accept(self, request, **kwargs):
        """ Accept the TOS

        .. note::

           Do *not* enable authentication handling here; we need
           people to do this using the UI.

        """
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)

        meta = models.UserMetadata.get_for_user(request.user)
        meta.tos_version = request.POST['version']
        meta.tos_accepted = now()
        meta.save()

        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @process_authentication()
    def email_integration(self, request, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)

        ts = models.TaskStore.get_for_user(request.user)
        ts.email_whitelist = request.POST.get('email_whitelist', '')
        ts.log_message("Email integration settings changed.")
        ts.save()

        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @process_authentication()
    def twilio_integration(self, request, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)

        ts = models.TaskStore.get_for_user(request.user)
        ts.twilio_auth_token = request.POST.get('twilio_auth_token', '')
        ts.sms_whitelist = request.POST.get('sms_whitelist', '')
        ts.sms_arguments = request.POST.get('sms_arguments', '')
        ts.sms_replies = request.POST.get('sms_replies', 9)
        ts.log_message("Twilio settings changed.")
        ts.save()
        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @git_managed("Clearing task data", gc=False)
    @process_authentication()
    def clear_task_data(self, request, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)

        ts = models.TaskStore.get_for_user(request.user)
        ts.clear_taskserver_data()

        for path in os.listdir(ts.local_path):
            if os.path.splitext(path)[1] == '.data':
                os.unlink(
                    os.path.join(
                        ts.local_path,
                        path
                    )
                )

        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @git_managed("Generating new certificate", gc=False)
    @process_authentication()
    def generate_new_certificate(self, request, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)
        ts = models.TaskStore.get_for_user(request.user)
        ts.generate_new_certificate()
        return HttpResponse(
            json.dumps({
                'message': 'OK',
            }),
            content_type='application/json',
        )

    @process_authentication()
    def my_certificate(self, request, **kwargs):
        if request.method != 'GET':
            return HttpResponseNotAllowed(request.method)
        ts = models.TaskStore.get_for_user(request.user)
        return self._send_file(
            ts.taskrc.get('taskd.certificate'),
            content_type='application/x-pem-file',
        )

    @process_authentication()
    def my_key(self, request, **kwargs):
        if request.method != 'GET':
            return HttpResponseNotAllowed(request.method)
        ts = models.TaskStore.get_for_user(request.user)
        return self._send_file(
            ts.taskrc.get('taskd.key'),
            content_type='application/x-pem-file',
        )

    @process_authentication()
    def ca_certificate(self, request, **kwargs):
        if request.method != 'GET':
            raise HttpResponseNotAllowed(request.method)
        ts = models.TaskStore.get_for_user(request.user)
        return self._send_file(
            ts.taskrc.get('taskd.ca'),
            content_type='application/x-pem-file',
        )

    @git_managed("Updating custom taskrc configuration", gc=False)
    @process_authentication()
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

    @process_authentication(required=False)
    def announcements(self, request, **kwargs):
        announcements = []

        if request.user.is_authenticated():
            for announcement in models.Announcement.current.all():
                announcements.append({
                    'type': announcement.category,
                    'title': announcement.title,
                    'duration': announcement.duration * 1000,
                    'message': announcement.message,
                })

            store = models.TaskStore.get_for_user(request.user)
            if not store.sync_enabled:
                announcements.append({
                    'type': 'error',
                    'title': 'Synchronization Disabled',
                    'duration': 5 * 60 * 1000,
                    'message': textwrap.dedent("""
                        Synchronization is currently disabled for your account
                        because we had trouble connecting to the Taskd server
                        you've asked us to use.  To re-enable synchronization,
                        please take a moment to verify the Taskd server
                        settings you've entered into your
                        <a href='/configure/'>configuration</a>.
                    """).strip().replace('\n', ' '),
                })
        return HttpResponse(
            json.dumps(announcements),
            content_type='application/json',
        )

    @process_authentication(required=False)
    def account_status(self, request, **kwargs):
        if request.user.is_authenticated():
            store = models.TaskStore.get_for_user(request.user)
            meta = models.UserMetadata.get_for_user(request.user)
            user_data = get_published_properties(request.user, store, meta)
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
