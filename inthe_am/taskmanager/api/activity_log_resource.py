from tastypie import authentication, resources

from .. import models
from .authorizations import TaskStoreAuthorization
from .mixins import LockTimeoutMixin


class ActivityLogResource(LockTimeoutMixin, resources.ModelResource):
    class Meta:
        resource_name = 'activityLog'
        queryset = models.TaskStoreActivityLog.objects.order_by('-last_seen')
        authorization = TaskStoreAuthorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = authentication.MultiAuthentication(
            authentication.ApiKeyAuthentication(),
            authentication.SessionAuthentication(),
        )
        filter_fields = [
            'last_seen',
            'created',
            'error',
            'message',
            'count'
        ]
        limit = 25
        max_limit = 400
