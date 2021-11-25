import datetime
import json
import logging
import urllib.parse

from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from .models import (
    Announcement,
    TaskAttachment,
    TaskStore,
    TaskStoreActivityLog,
    TrelloObject,
    TrelloObjectAction,
    TaskStoreStatistic,
    UserMetadata,
)


logger = logging.getLogger(__name__)


class DefaultFilterMixIn(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        full_path = request.get_full_path()
        path_info = urllib.parse.urlparse(full_path)
        referrer = request.META.get("HTTP_REFERER", "")
        if path_info.path not in referrer:
            q = request.GET.copy()
            try:
                for key, value in self.default_filters.items():
                    q[key] = str(value)
                request.GET = q
            except Exception:
                request.GET = q
            request.META["QUERY_STRING"] = request.GET.urlencode()
        return super().changelist_view(request, extra_context=extra_context)


class ActivityStatusListFilter(admin.SimpleListFilter):
    title = "activity status"
    parameter_name = "activity_status"

    def lookups(self, request, model_admin):
        return (
            ("1", "1 day"),
            ("2", "2 days"),
            ("3", "3 days"),
            ("7", "7 days"),
            ("30", "30 days"),
            ("90", "90 days"),
        )

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except (ValueError, TypeError):
            return queryset

        return queryset.filter(last_synced__gte=now() - datetime.timedelta(days=value))


class RegistrationRecency(admin.SimpleListFilter):
    title = "membership"
    parameter_name = "registration_recency"

    def lookups(self, request, model_admin):
        return (
            ("1", "at least 1 days"),
            ("2", "at least 2 days"),
            ("3", "at least 3 days"),
            ("7", "at least 7 days"),
            ("30", "at least 30 days"),
            ("90", "at least 90 days"),
        )

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except (ValueError, TypeError):
            return queryset

        return queryset.filter(created__lte=now() - datetime.timedelta(days=value))


class TrelloEnabledFilter(admin.SimpleListFilter):
    title = "trello enabled"
    parameter_name = "trello_enabled"

    def lookups(self, request, model_admin):
        return (
            (
                "1",
                "Yes",
            ),
            (
                "0",
                "No",
            ),
        )

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except (ValueError, TypeError):
            return queryset

        if value:
            return queryset.exclude(trello_auth_token="")
        else:
            return queryset.filter(trello_auth_token="")


class TwilioEnabledFilter(admin.SimpleListFilter):
    title = "twilio enabled"
    parameter_name = "twilio_enabled"

    def lookups(self, request, model_admin):
        return (
            (
                "1",
                "Yes",
            ),
            (
                "0",
                "No",
            ),
        )

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except (ValueError, TypeError):
            return queryset

        if value:
            return queryset.exclude(twilio_auth_token="")
        else:
            return queryset.filter(twilio_auth_token="")


class TaskStoreStatisticAdmin(admin.ModelAdmin):
    raw_id_fields = ("store",)
    search_fields = ("store__user__username",)
    list_display = ("created", "store", "username", "measure", "value")
    list_filter = ("measure",)
    ordering = ("-created",)

    def username(self, obj):
        return obj.store.user.username


admin.site.register(TaskStoreStatistic, TaskStoreStatisticAdmin)


class TaskStoreAdmin(DefaultFilterMixIn, admin.ModelAdmin):
    raw_id_fields = ("user",)
    search_fields = (
        "user__username",
        "local_path",
        "taskrc_extras",
        "sms_whitelist",
        "email_whitelist",
        "secret_id",
    )
    list_display = (
        "user",
        "created",
        "last_synced",
        "sync_enabled",
        "pebble_cards_enabled",
        "feed_enabled",
        "ical_enabled",
        "twilio_enabled",
        "trello_enabled",
        "local_sync",
    )
    list_filter = (
        ActivityStatusListFilter,
        RegistrationRecency,
        TrelloEnabledFilter,
        TwilioEnabledFilter,
        "created",
        "last_synced",
        "sync_enabled",
        "pebble_cards_enabled",
        "ical_enabled",
        "feed_enabled",
    )
    ordering = ("-last_synced",)
    readonly_fields = (
        "local_path",
        "last_synced",
        "metadata",
        "taskrc",
    )
    default_filters = {
        "activity_status": "7",
        "registration_recency": "30",
    }

    def _renderable(self, value):
        return mark_safe(
            json.dumps(dict(value), indent=4, sort_keys=True).replace(" ", "&nbsp;")
        )

    def metadata(self, store):
        if store.pk:
            return self._renderable(store.metadata)
        return ""

    def taskrc(self, store):
        if store.pk:
            return self._renderable(store.taskrc)
        return ""

    def twilio_enabled(self, store):
        return True if store.twilio_auth_token else False

    twilio_enabled.boolean = True  # type: ignore

    def trello_enabled(self, store):
        return True if store.trello_auth_token else False

    trello_enabled.boolean = True  # type: ignore

    def local_sync(self, store):
        try:
            return store.sync_uses_default_server
        except Exception as e:
            logger.exception(e)
            return None

    local_sync.boolean = True  # type: ignore


admin.site.register(TaskStore, TaskStoreAdmin)


class TaskAttachmentAdmin(admin.ModelAdmin):
    raw_id_fields = ("store",)
    search_fields = (
        "store__user__username",
        "task_id",
        "name",
    )
    list_filter = ("created",)
    list_display = (
        "store",
        "task_id",
        "name",
        "size",
        "created",
    )
    ordering = ("-created",)


admin.site.register(TaskAttachment, TaskAttachmentAdmin)


class TaskStoreActivityLogAdmin(DefaultFilterMixIn, admin.ModelAdmin):
    raw_id_fields = ("store",)
    search_fields = ("store__user__username", "message", "store__local_path")
    list_display = ("username", "last_seen", "created", "error", "message", "count")
    date_hierarchy = "last_seen"
    list_filter = (
        "error",
        "created",
        "last_seen",
    )
    list_select_related = True
    ordering = ("-last_seen",)
    default_filters = {
        "error__exact": 1,
    }

    def username(self, obj):
        return obj.store.username

    username.short_description = "Username"  # type: ignore


admin.site.register(TaskStoreActivityLog, TaskStoreActivityLogAdmin)


class UserMetadataAdmin(admin.ModelAdmin):
    search_fields = ("user__username",)
    list_display = (
        "user",
        "tos_version",
        "tos_accepted",
    )
    list_filter = ("tos_version",)
    raw_id_fields = ("user",)


admin.site.register(UserMetadata, UserMetadataAdmin)


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "duration",
        "starts",
        "expires",
    )
    list_filter = (
        "category",
        "starts",
        "expires",
    )
    search_fields = (
        "title",
        "category",
    )


admin.site.register(Announcement, AnnouncementAdmin)


class TrelloObjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "store",
        "type",
        "created",
        "updated",
    )
    list_filter = ("type",)
    search_fields = (
        "id",
        "store__user__username",
    )
    raw_id_fields = (
        "store",
        "parent",
    )
    ordering = ("-updated",)
    date_hierarchy = "updated"


admin.site.register(TrelloObject, TrelloObjectAdmin)


class TrelloObjectActionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "action_id",
        "type",
        "model",
        "occurred",
    )
    list_filter = ("type",)
    search_fields = (
        "id",
        "action_id",
        "model__id",
        "model__store__user__username",
    )
    raw_id_fields = ("model",)
    ordering = ("-occurred",)
    list_select_related = True
    date_hierarchy = "occurred"


admin.site.register(TrelloObjectAction, TrelloObjectActionAdmin)


class TaskStoreActivityStatusListFilter(admin.SimpleListFilter):
    title = "failed/incomplete"
    parameter_name = "failed_incomplete"

    def lookups(self, request, model_admin):
        return (
            (
                "no",
                "Exclude Failed/Incomplete",
            ),
        )

    def queryset(self, request, queryset):
        if self.value() == "no":
            return queryset.exclude(duration_seconds=None)
        return queryset
