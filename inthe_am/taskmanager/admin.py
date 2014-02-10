from django.contrib import admin

from .models import TaskStore


class TaskStoreAdmin(admin.ModelAdmin):
    model = TaskStore
    search_fields = ('user__username', 'local_path', 'taskrc_extras', )
    list_display = ('user', 'local_path', 'configured', )
    list_filter = ('configured', )


admin.site.register(TaskStore, TaskStoreAdmin)
