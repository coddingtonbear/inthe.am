import os
import textwrap

from django import http
from django.conf import settings
from django.core.signing import Signer
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .. import exceptions, models
from ..decorators import git_managed, requires_task_store
from ..serializers.user import UserSerializer


URLS = {
    "login": "/login/google-oauth2/",
    "logout": "/logout/",
    "about": "/about/",
    "generate_new_certificate": "/api/v2/user/generate-new-certificate/",
    "ca_certificate": "/api/v2/user/ca-certificate/",
    "my_certificate": "/api/v2/user/my-certificate/",
    "my_key": "/api/v2/user/my-key/",
    "taskrc_extras": "/api/v2/user/taskrc/",
    "taskd_settings": "/api/v2/user/configure-taskd/",
    "taskd_reset": "/api/v2/user/reset-taskd-configuration/",
    "email_integration": "/api/v2/user/email-integration/",
    "twilio_integration": "/api/v2/user/twilio-integration/",
    "tos_accept": "/api/v2/user/tos-accept/",
    "privacy_policy_accept": "/api/v2/user/privacy-policy-accept/",
    "clear_task_data": "/api/v2/user/clear-task-data/",
    "delete_account": "/api/v2/user/delete-account/",
    "set_colorscheme": "/api/v2/user/colorscheme/",
    "enable_sync": "/api/v2/user/enable-sync/",
    "mirakel_configuration": "/api/v2/user/mirakel-configuration/",
    "configure_pebble_cards": "/api/v2/user/pebble-cards-config/",
    "configure_feed": "/api/v2/user/feed-config/",
    "configure_ical": "/api/v2/user/ical-config/",
    "user_status": "/api/v2/user/status/",
    "announcements": "/api/v2/user/announcements/",
    "refresh": "/api/v2/tasks/refresh/",
    "clear_lock": "/api/v2/tasks/lock/",
    "sync_init": "/api/v2/tasks/sync-init/",
    "revert_to_last_commit": "/api/v2/tasks/revert/",
    "sync": "/api/v2/tasks/sync/",
    "trello_authorization_url": "/api/v2/tasks/trello/",
    "trello_resynchronization_url": "/api/v2/tasks/trello/resynchronize/",
    "trello_reset_url": "/api/v2/tasks/trello/reset/",
    "deduplicate_tasks": "/api/v2/tasks/deduplicate/",
    "deduplication_config": "/api/v2/tasks/deduplication-config/",
    "status_feed": "/status/",
}


def get_published_properties(user, store, meta):
    signer = Signer()

    data = {
        "logged_in": True,
        "uid": user.pk,
        "username": user.username,
        "name": (user.first_name if user.first_name else user.username),
        "email": user.email,
        "configured": store.configured,
        "taskd_credentials": store.taskrc.get("taskd.credentials"),
        "taskd_server": store.taskrc.get("taskd.server"),
        "taskd_server_is_default": store.sync_uses_default_server,
        "streaming_enabled": (
            settings.STREAMING_UPDATES_ENABLED and store.sync_uses_default_server
        ),
        "streaming_key": signer.sign(str(store.pk)),
        "taskd_files": store.taskd_certificate_status,
        "twilio_auth_token": store.twilio_auth_token,
        "sms_whitelist": store.sms_whitelist,
        "sms_arguments": store.sms_arguments,
        "sms_replies": store.sms_replies,
        "email_whitelist": store.email_whitelist,
        "task_creation_email_address": f"{store.secret_id}@inthe.am",
        "taskrc_extras": store.taskrc_extras,
        "api_key": store.api_key.key,
        "tos_up_to_date": meta.tos_up_to_date,
        "privacy_policy_up_to_date": meta.privacy_policy_up_to_date,
        "feed_url": reverse(
            "feed",
            kwargs={
                "uuid": store.secret_id,
            },
        ),
        "ical_waiting_url": reverse(
            "ical_feed",
            kwargs={
                "variant": "waiting",
                "secret_id": store.secret_id,
            },
        ),
        "ical_due_url": reverse(
            "ical_feed",
            kwargs={
                "variant": "due",
                "secret_id": store.secret_id,
            },
        ),
        "sms_url": reverse(
            "incoming_sms",
            kwargs={
                "username": user.username,
            },
        ),
        "colorscheme": meta.colorscheme,
        "repository_head": store.repository.head().decode("utf-8"),
        "sync_enabled": store.sync_enabled,
        "pebble_cards_enabled": store.pebble_cards_enabled,
        "feed_enabled": store.feed_enabled,
        "ical_enabled": store.ical_enabled,
        "auto_deduplicate": store.auto_deduplicate,
        "trello_board_url": (
            store.trello_board.meta["url"] if store.trello_board else None
        ),
        "system_udas": get_system_udas_as_uda_list(),
        "urls": URLS,
    }

    try:
        data.update(
            {
                "udas": [
                    {"field": k, "label": v.label, "type": v.__class__.__name__}
                    for k, v in store.client.config.get_udas().items()
                ],
            }
        )
    except exceptions.InvalidTaskwarriorConfiguration:
        pass

    return data


def get_system_udas_as_uda_list():
    overrides = []
    config_overrides = settings.TASKWARRIOR_CONFIG_OVERRIDES["uda"]
    for uda_name, uda_properties in config_overrides.items():
        overrides.append(
            {
                "field": uda_name,
                "label": uda_properties.get("label", ""),
                "type": uda_properties.get("type", ""),
            }
        )

    return overrides


class UserViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        serializer = UserSerializer([request.user], many=True)
        return Response(serializer.data)

    def retrieve(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def _send_file(
        self,
        filepath,
        content_type: str = "application/octet-stream",
        filename: str = None,
    ):
        if filepath is None or not os.path.isfile(filepath):
            raise NotFound()

        with open(filepath, "r") as outfile:
            response = http.HttpResponse(outfile.read(), content_type=content_type)
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{filename or os.path.basename(filepath)}"'
            return response

    @action(detail=False, methods=["get"])
    def status(self, request):
        if request.user.is_authenticated():
            store = models.TaskStore.get_for_user(request.user)
            meta = models.UserMetadata.get_for_user(request.user)
            user_data = get_published_properties(request.user, store, meta)
        else:
            user_data = {
                "logged_in": False,
                "urls": URLS,
            }

        return Response(user_data)

    @action(detail=False, methods=["get"])
    def announcements(self, request):
        announcements = []

        if request.user.is_authenticated():
            for announcement in models.Announcement.current.all():
                announcements.append(
                    {
                        "type": announcement.category,
                        "title": announcement.title,
                        "duration": announcement.duration * 1000,
                        "message": announcement.message,
                    }
                )

            store = models.TaskStore.get_for_user(request.user)
            if not store.sync_enabled:
                announcements.append(
                    {
                        "type": "error",
                        "title": "Synchronization Disabled",
                        "duration": 5 * 60 * 1000,
                        "message": textwrap.dedent(
                            """
                        Synchronization is currently disabled for your account
                        because we had trouble connecting to the Taskd server
                        you've asked us to use.  To re-enable synchronization,
                        please take a moment to verify the Taskd server
                        settings you've entered into your
                        <a href='/configure/'>configuration</a>.
                    """
                        )
                        .strip()
                        .replace("\n", " "),
                    }
                )

        return Response(announcements)

    @git_managed("Generate new certificate", gc=False)
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="generate-new-certificate",
    )
    def generate_new_certificate(
        self, request: http.HttpRequest, store: models.TaskStore
    ):
        store.generate_new_certificate()
        return Response()

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="my-certificate",
    )
    def my_certificate(self, request):
        ts = models.TaskStore.get_for_user(request.user)
        return self._send_file(
            ts.taskrc.get("taskd.certificate"),
            content_type="application/x-pem-file",
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="my-key",
    )
    def my_key(self, request):
        ts = models.TaskStore.get_for_user(request.user)
        return self._send_file(
            ts.taskrc.get("taskd.key"),
            content_type="application/x-pem-file",
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="ca-certificate",
    )
    def ca_certificate(self, request):
        ts = models.TaskStore.get_for_user(request.user)
        return self._send_file(
            ts.taskrc.get("taskd.ca"),
            content_type="application/x-pem-file",
            filename="ca.cert.pem",
        )

    @git_managed("Update custom taskrc configuration", gc=False)
    @action(
        detail=False,
        methods=[
            "get",
            "put",
        ],
        permission_classes=[IsAuthenticated],
    )
    def taskrc(self, request, store=None):
        if request.method == "GET":
            store = models.TaskStore.get_for_user(request.user)
            return Response(store.taskrc_extras, content_type="text/plain")
        elif request.method == "PUT":
            store = models.TaskStore.get_for_user(request.user)
            store.taskrc_extras = request.body.decode(
                request.encoding if request.encoding else "utf-8"
            )
            results = store.apply_extras()
            store.save()
            store.log_message("Taskrc extras saved.")
            return Response({"success": results[0], "failed": results[1]})

    @git_managed("Reset taskd configuration", gc=False)
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="reset-taskd-configuration",
    )
    def reset_taskd_configuration(self, request, store=None):
        store.reset_taskd_configuration()
        return Response()

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="tos-accept",
    )
    def tos_accept(self, request):
        meta = models.UserMetadata.get_for_user(request.user)
        meta.tos_version = int(request.POST["version"])
        meta.tos_accepted = now()
        meta.save()

        return Response()

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="privacy-policy-accept",
    )
    def privacy_policy_accept(self, request):
        meta = models.UserMetadata.get_for_user(request.user)
        meta.privacy_policy_version = int(request.POST["version"])
        meta.privacy_policy_accepted = now()
        meta.save()

        return Response()

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="twilio-integration",
    )
    def twilio_integration(self, request):
        ts = models.TaskStore.get_for_user(request.user)
        ts.twilio_auth_token = request.POST.get("twilio_auth_token", "")
        ts.sms_whitelist = request.POST.get("sms_whitelist", "")
        ts.sms_arguments = request.POST.get("sms_arguments", "")
        ts.sms_replies = request.POST.get("sms_replies", 9)
        ts.log_message("Twilio settings changed.")
        ts.save()

        return Response()

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="email-integration",
    )
    def email_integration(self, request):
        ts = models.TaskStore.get_for_user(request.user)
        ts.email_whitelist = request.POST.get("email_whitelist", "")
        ts.log_message("Email integration settings changed.")
        ts.save()

        return Response()

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="clear-task-data",
    )
    def clear_task_data(self, request):
        ts = models.TaskStore.get_for_user(request.user)
        ts.clear_taskserver_data()
        ts.clear_local_task_list()

        return Response()

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="delete-account",
    )
    def delete_account(self, request):
        ts = models.TaskStore.get_for_user(request.user)
        ts.delete(raise_for_failure=True)

        return Response()

    @action(
        detail=False,
        methods=["put", "get"],
        permission_classes=[IsAuthenticated],
    )
    def colorscheme(self, request):
        meta = models.UserMetadata.get_for_user(request.user)
        if request.method == "PUT":
            meta.colorscheme = request.body
            meta.save()

            return Response()
        elif request.method == "GET":
            return Response(
                meta,
                content_type="text/plain",
            )

    @requires_task_store
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="enable-sync",
    )
    def enable_sync(self, request, store=None):
        if not store.sync_permitted:
            raise PermissionDenied(
                "Synchronization cannot be enabled for your account; "
                "please contact admin@inthe.am for more information."
            )
        store.sync_enabled = True
        store.save()

        return Response()

    @requires_task_store
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="feed-config",
    )
    def feed_config(self, request, store=None):
        try:
            enabled = int(request.POST.get("enabled", 0))
        except (TypeError, ValueError):
            return Response(status=400)

        store = models.TaskStore.get_for_user(request.user)
        store.feed_enabled = True if enabled else False
        store.save()

        return Response()

    @requires_task_store
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="ical-config",
    )
    def ical_config(self, request, store=None):
        try:
            enabled = int(request.POST.get("enabled", 0))
        except (TypeError, ValueError):
            return Response(status=400)

        store = models.TaskStore.get_for_user(request.user)
        store.ical_enabled = True if enabled else False
        store.save()

        return Response()
