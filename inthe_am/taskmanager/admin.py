import datetime
import json
import urlparse

from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from .models import (
    Announcement,
    TaskAttachment,
    TaskStore,
    TaskStoreActivityLog,
    UserMetadata
)


class DefaultFilterMixIn(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        full_path = request.get_full_path()
        path_info = urlparse.urlparse(full_path)
        referrer = request.META.get('HTTP_REFERER', '')
        if not path_info.path in referrer:
            q = request.GET.copy()
            try:
                for key, value in self.default_filters.items():
                    q[key] = str(value)
                request.GET = q
            except:
                request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(DefaultFilterMixIn, self).changelist_view(
            request, extra_context=extra_context
        )


class ActivityStatusListFilter(admin.SimpleListFilter):
    title = 'activity status'
    parameter_name = 'activity_status'

    def lookups(self, request, model_admin):
        return (
            ('1', '1 day'),
            ('2', '2 days'),
            ('3', '3 days'),
            ('7', '7 days'),
            ('30', '30 days'),
            ('90', '90 days'),
        )

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except (ValueError, TypeError):
            return queryset

        return queryset.filter(
            last_synced__gte=now() - datetime.timedelta(days=value)
        )


class RegistrationRecency(admin.SimpleListFilter):
    title = 'membership'
    parameter_name = 'registration_recency'

    def lookups(self, request, model_admin):
        return (
            ('1', 'at least 1 days'),
            ('2', 'at least 2 days'),
            ('3', 'at least 3 days'),
            ('7', 'at least 7 days'),
            ('30', 'at least 30 days'),
            ('90', 'at least 90 days'),
        )

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except (ValueError, TypeError):
            return queryset

        return queryset.filter(
            created__lte=now() - datetime.timedelta(days=value)
        )


class TwilioEnabledFilter(admin.SimpleListFilter):
    title = 'twilio_enabled'
    parameter_name = 'twilio_enabled'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yes', ),
            ('0', 'No', ),
        )

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except (ValueError, TypeError):
            return queryset

        if value:
            return queryset.exclude(
                twilio_auth_token=''
            )
        else:
            return queryset.filter(
                twilio_auth_token=''
            )


class TaskStoreAdmin(DefaultFilterMixIn, admin.ModelAdmin):
    raw_id_fields = ('user', )
    search_fields = (
        'user__username', 'local_path', 'taskrc_extras',
        'sms_whitelist', 'email_whitelist',
    )
    list_display = (
        'user', 'created', 'last_synced',
        'sync_enabled', 'pebble_cards_enabled', 'feed_enabled',
        'twilio_enabled',
    )
    list_filter = (
        ActivityStatusListFilter,
        RegistrationRecency,
        TwilioEnabledFilter,
        'created', 'last_synced',
        'sync_enabled', 'pebble_cards_enabled', 'feed_enabled',
    )
    ordering = ('-last_synced', )
    readonly_fields = (
        'local_path',
        'last_synced',
        'metadata',
        'taskrc',
    )
    default_filters = {
        'activity_status': '7',
        'registration_recency': '30',
    }

    def _renderable(self, value):
        return mark_safe(
            json.dumps(
                dict(value),
                indent=4,
                sort_keys=True
            ).replace(' ', '&nbsp;')
        )

    def metadata(self, store):
        return self._renderable(store.metadata)

    def taskrc(self, store):
        return self._renderable(store.taskrc)

    def twilio_enabled(self, store):
        return True if self.twilio_auth_token else False
    twilio_enabled.boolean = True

admin.site.register(TaskStore, TaskStoreAdmin)


class TaskAttachmentAdmin(admin.ModelAdmin):
    raw_id_fields = ('store', )
    search_fields = (
        'store__user__username', 'task_id', 'name',
    )
    list_filter = (
        'created',
    )
    list_display = (
        'store',
        'task_id',
        'name',
        'size',
        'created',
    )
    ordering = ('-created', )


admin.site.register(TaskAttachment, TaskAttachmentAdmin)


class TaskStoreActivityLogAdmin(DefaultFilterMixIn, admin.ModelAdmin):
    raw_id_fields = ('store', )
    search_fields = (
        'store__user__username', 'message', 'store__local_path'
    )
    list_display = (
        'username', 'last_seen', 'created', 'error', 'message', 'count'
    )
    date_hierarchy = 'last_seen'
    list_filter = ('error', 'created', 'last_seen', )
    list_select_related = True
    ordering = ('-last_seen', )
    default_filters = {
        'error__exact': 1,
    }

    def username(self, obj):
        return obj.store.user.username
    username.short_description = 'Username'


admin.site.register(TaskStoreActivityLog, TaskStoreActivityLogAdmin)


class UserMetadataAdmin(admin.ModelAdmin):
    search_fields = ('user__username', )
    list_display = ('user', 'tos_version', 'tos_accepted', )
    list_filter = ('tos_version', )
    raw_id_fields = ('user', )


admin.site.register(UserMetadata, UserMetadataAdmin)


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'duration', 'starts', 'expires', )
    list_filter = ('category', 'starts', 'expires', )
    search_fields = ('title', 'category', )

admin.site.register(Announcement, AnnouncementAdmin)
