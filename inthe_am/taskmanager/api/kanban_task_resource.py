import json
import re

from tastypie.utils import trailing_slash
from tastypie import authorization

from django.conf.urls import url
from django.core.exceptions import PermissionDenied
from django.forms import EmailField, ValidationError
from django.http import HttpResponse, HttpResponseNotAllowed

from ..models import KanbanBoard, KanbanMembership
from ..decorators import requires_task_store
from .kanban_membership_resource import KanbanMembershipResource
from .task_resource import TaskResource


class KanbanTaskResource(TaskResource):
    BOARD_ID_RE = re.compile(
        r"/api/v1/kanban/(?P<uuid>[^/]+)/"
    )

    def prepend_urls(self):
        return [
            url(
                r"^members/invite/?$",
                self.wrap_view('members_invite'),
                name='kanban_members_invite',
            ),
            url(
                r"^members/respond/?$",
                self.wrap_view('members_respond'),
                name='kanban_members_respond',
            ),
            url(
                r"^members/(?P<member_uuid>[\w\d_.-]+)/?$",
                self.wrap_view('members_detail'),
                name='kanban_members_detail',
            ),
            url(
                r"^members/?$",
                self.wrap_view('members_list'),
                name='kanban_members_list',
            ),
            url(
                r"^meta/?$",
                self.wrap_view('kanban_meta'),
                name='kanban_meta',
            ),
        ]

    def base_urls(self):
        """ Returns default base URLs.

        Note: this overrides the generic behavior because rather than using
        urls like ``/api/v1/task/<id>/``, we'll instead be using urls like
        ``/api/v1/kanban/<uuid>/<id>`` where <uuid> is the ID of the kanban
        board itself.

        """
        return [
            url(
                r"^$",
                self.wrap_view('dispatch_list'),
                name="api_dispatch_list"
            ),
            url(
                r"^schema%s$" % (trailing_slash(), ),
                self.wrap_view('get_schema'),
                name="api_get_schema"
            ),
            url(
                r"^set/(?P<%s_list>.*?)%s$" % (
                    self._meta.detail_uri_name,
                    trailing_slash(),
                ),
                self.wrap_view('get_multiple'),
                name="api_get_multiple"
            ),
            url(
                r"^(?P<%s>.*?)%s$" % (
                    self._meta.detail_uri_name,
                    trailing_slash(),
                ),
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"
            ),
        ]

    @requires_task_store
    def members_list(self, request, store, **kwargs):
        resource = KanbanMembershipResource(store)

        if request.method == 'GET':
            return resource.get_list(request)

        return HttpResponseNotAllowed(request.method)

    @requires_task_store
    def members_detail(self, request, store, **kwargs):
        resource = KanbanMembershipResource(store)

        if request.method == 'DELETE':
            record = store.memberships.get(
                uuid=kwargs['member_uuid'],
                kanban_board=store,
            )
            if not (
                record.member == request.user or
                store.user_is_owner(request.user)
            ):
                raise PermissionDenied()
            return resource.delete_detail(request, uuid=kwargs['member_uuid'])
        elif request.method == 'GET':
            return resource.get_detail(request, uuid=kwargs['member_uuid'])

        return HttpResponseNotAllowed(request.method)

    @requires_task_store
    def members_invite(self, request, store, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)

        email = request.POST.get('email')
        validator = EmailField()
        try:
            validator.clean(email)
        except ValidationError:
            return HttpResponse(
                json.dumps({
                    'error_message': 'Invalid e-mail address',
                }),
                status=400,
            )

        role = request.POST.get('role')
        if role not in [v for v, _ in KanbanMembership.ROLES]:
            return HttpResponse(
                json.dumps({
                    'error_message': 'Invalid role',
                }),
                status=400,
            )

        KanbanMembership.invite_user(
            board=store,
            sender=request.user,
            email=email,
            role=role,
        )
        return HttpResponse(
            json.dumps({
                'message': 'Membership sent; pending acceptance.'
            }),
            status=200,
        )

    def members_respond(self, request, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(request.method)

        invitation_id = request.POST.get('uuid')
        accepted = bool(int(request.POST.get('accepted', 0)))

        try:
            membership = KanbanMembership.objects.get(
                member=None,
                valid=True,
                uuid=invitation_id,
            )
        except:
            return HttpResponse(
                json.dumps({
                    'error_message': (
                        'The invitation ID you specified is invalid.'
                    )
                }),
                status=400,
            )

        membership.member = request.user
        membership.accepted = accepted
        if not accepted:
            membership.valid = False
        membership.save()

        if accepted:
            KanbanMembership.objects.filter(
                member=request.user,
                kanban_board=membership.kanban_board
            ).exclude(
                pk=membership.pk
            ).update(valid=False)

        return HttpResponse(
            json.dumps({
                'message': (
                    'Invitation accepted'
                    if accepted
                    else 'Invitation rejected'
                )
            }),
            status=200
        )

    def meta(self, store):
        return {
            'id': store.uuid,
            'name': store.name,
            'columns': json.loads(store.columns),
        }

    def set_meta(self, store, value):
        store.name = value['name']
        store.columns = json.dumps(
            value['columns']
        )
        store.save()

    @requires_task_store
    def kanban_meta(self, request, store, **kwargs):
        if request.method == 'GET':
            return HttpResponse(
                json.dumps(self.meta(store)),
                content_type='application/json',
            )
        elif request.method == 'PUT':
            self.set_meta(
                store,
                self.deserialize(
                    request,
                    request.body,
                    format=request.META.get(
                        'CONTENT_TYPE', 'application/json'
                    )
                )
            )
            return HttpResponse(
                json.dumps(self.meta),
                content_type='application/json',
            )

        return HttpResponseNotAllowed(request.method)

    def passes_filters(self, task, filters):
        """ Filters are not currently supported for KanbanTask items."""
        return True

    def get_task_store(self, request):
        board = KanbanBoard.objects.get(
            uuid=self.BOARD_ID_RE.search(request.path).group('uuid')
        )
        if not board.user_is_member(request.user):
            raise PermissionDenied()

        return board

    class Meta(TaskResource.Meta):
        resource_name = 'kanbanTask'
        authorization = authorization.Authorization()
