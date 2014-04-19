from django.contrib import admin

from .models import TaskStore, TaskStoreActivityLog, UserMetadata


class TaskStoreAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'local_path', 'taskrc_extras', )
    list_display = ('user', 'created', 'sync_enabled', 'twilio_enabled')
    list_filter = ('configured', )

    def twilio_enabled(self, obj):
        return obj.twilio_auth_token

admin.site.register(TaskStore, TaskStoreAdmin)


class TaskStoreActivityLogAdmin(admin.ModelAdmin):
    search_fields = ('store__user__username', 'message', )
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
