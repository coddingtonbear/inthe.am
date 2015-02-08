from tastypie import authentication

from .task_resource import TaskResource


class CompletedTaskResource(TaskResource):
    TASK_TYPE = 'completed'

    class Meta:
        always_return_data = True
        authentication = authentication.MultiAuthentication(
            authentication.SessionAuthentication(),
            authentication.ApiKeyAuthentication(),
        )
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filter_fields = [
            'status',
            'due',
            'entry',
            'id',
            'imask',
            'modified',
            'parent',
            'recur',
            'status',
            'urgency',
            'uuid',
            'wait',
        ]
        limit = 100
        max_limit = 400
