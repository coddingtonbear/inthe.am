import json

from tastypie import authentication, authorization, bundle, resources

from django.conf.urls import url
from django.contrib.auth.models import User
from django.http import HttpResponse


class UserAuthorization(authorization.Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(
            pk=bundle.request.user.pk
        )

    def read_detail(self, object_list, bundle):
        return bundle.obj == bundle.request.user


class UserResource(resources.ModelResource):
    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>%s)/status/?$" % (
                    self._meta.resource_name
                ),
                self.wrap_view('account_status')
            ),
        ]

    def account_status(self, request, **kwargs):
        if request.user.is_authenticated():
            user_data = {
                'logged_in': True,
                'uid': request.user.pk,
                'username': request.user.username,
                'name': (
                    request.user.first_name
                    if request.user.first_name
                    else request.user.username
                ),
                'email': request.user.email,
                'dropbox_configured': request.user.task_stores.count() > 0
            }
        else:
            user_data = {
                'logged_in': False,
            }
        return HttpResponse(
            json.dumps(user_data),
            content_type='application/json',
        )

    class Meta:
        queryset = User.objects.all()
        authorization = UserAuthorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']


class TaskResource(resources.Resource):
    def _get_config_for_user(self, user):
        user.task_stores.get()

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, bundle.Bundle):
            kwargs['pk'] = bundle_or_obj.obj['uuid']
        else:
            kwargs['pk'] = bundle_or_obj['uuid']

        return kwargs

    def get_object_list(self, request):
        pass

    class Meta:
        authentication = authentication.SessionAuthentication()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
