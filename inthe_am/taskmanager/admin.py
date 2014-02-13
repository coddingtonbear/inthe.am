from django.contrib import admin

from .models import TaskStore, UserMetadata


class TaskStoreAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'local_path', 'taskrc_extras', )
    list_display = ('user', 'local_path', 'configured', )
    list_filter = ('configured', )


admin.site.register(TaskStore, TaskStoreAdmin)


class UserMetadataAdmin(admin.ModelAdmin):
    search_fields = ('user__username', )
    list_display = ('user', 'tos_version', 'tos_accepted', )
    list_filter = ('tos_version', )


admin.site.register(UserMetadata, UserMetadataAdmin)
