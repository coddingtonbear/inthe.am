import urlparse

from django.contrib import admin

from .models import TaskStore, TaskStoreActivityLog, UserMetadata


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


class TaskStoreAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', )
    search_fields = (
        'user__username', 'local_path', 'taskrc_extras',
        'sms_whitelist', 'email_whitelist',
    )
    list_display = (
        'user', 'created', 'last_synced',
        'sync_enabled', 'pebble_cards_enabled', 'feed_enabled',
    )
    list_filter = (
        'created', 'last_synced',
        'sync_enabled', 'pebble_cards_enabled', 'feed_enabled',
    )
    ordering = ('-last_synced', )

admin.site.register(TaskStore, TaskStoreAdmin)


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
