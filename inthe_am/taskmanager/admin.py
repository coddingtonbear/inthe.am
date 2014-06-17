from django.contrib import admin

from .models import TaskStore, TaskStoreActivityLog, UserMetadata


class TaskStoreAdmin(admin.ModelAdmin):
    search_fields = (
        'user__username', 'local_path', 'taskrc_extras',
        'sms_whitelist', 'email_whitelist',
    )
    list_display = (
        'user', 'created', 'last_synced',
        'sync_enabled', 'pebble_cards_enabled', 'feed_enabled',
    )
    list_filter = (
        'sync_enabled', 'pebble_cards_enabled', 'feed_enabled',
    )

admin.site.register(TaskStore, TaskStoreAdmin)


class TaskStoreActivityLogAdmin(admin.ModelAdmin):
    search_fields = (
        'store__user__username', 'message', 'store__local_path'
    )
    list_display = (
        'username', 'last_seen', 'created', 'error', 'message', 'count'
    )
    date_hierarchy = 'last_seen'
    list_filter = ('created', 'last_seen', )
    list_select_related = True
    ordering = ('-last_seen', )

    def username(self, obj):
        return obj.store.user.username
    username.short_description = 'Username'


admin.site.register(TaskStoreActivityLog, TaskStoreActivityLogAdmin)


class UserMetadataAdmin(admin.ModelAdmin):
    search_fields = ('user__username', )
    list_display = ('user', 'tos_version', 'tos_accepted', )
    list_filter = ('tos_version', )


admin.site.register(UserMetadata, UserMetadataAdmin)
