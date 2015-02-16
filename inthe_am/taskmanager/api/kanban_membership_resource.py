from tastypie import authentication, authorization, resources

from django.core.urlresolvers import reverse

from .. import models
from .mixins import LockTimeoutMixin


class KanbanMembershipResource(LockTimeoutMixin, resources.ModelResource):
    def __init__(self, kanban_board, *args, **kwargs):
        self.kanban_board = kanban_board
        super(KanbanMembershipResource, self).__init__(
            *args, **kwargs
        )

    def get_object_list(self, request):
        return super(
            KanbanMembershipResource, self
        ).get_object_list(request).filter(
            kanban_board=self.kanban_board
        )

    def get_resource_uri(
        self, bundle_or_obj=None, url_name='api_dispatch_list'
    ):
        if bundle_or_obj:
            return reverse(
                'kanban_members_detail',
                kwargs={
                    'uuid': self.kanban_board.uuid,
                    'member_uuid': bundle_or_obj.obj.uuid
                }
            )
        return reverse(
            'kanban_members_list',
            kwargs={
                'uuid': self.kanban_board.uuid,
            }
        )

    def dehydrate(self, bundle):
        bundle.data['sender'] = {
            'first_name': bundle.obj.sender.first_name,
            'last_name': bundle.obj.sender.last_name,
            'email': bundle.obj.sender.email,
        }
        bundle.data['board'] = {
            'name': bundle.obj.kanban_board.name,
        }
        return bundle

    class Meta:
        resource_name = 'kanbanmembership'
        queryset = models.KanbanMembership.objects.all()
        authorization = authorization.Authorization()
        authentication = authentication.MultiAuthentication(
            authentication.ApiKeyAuthentication(),
            authentication.SessionAuthentication(),
        )
        filter_fields = [
            'uuid',
            'kanban_board',
            'sender',
            'member',
            'role',
            'accepted',
            'valid',
            'created',
            'updated',
        ]
        limit = 25
        max_limit = 400
