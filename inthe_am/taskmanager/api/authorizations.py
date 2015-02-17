from tastypie import authorization


class UserAuthorization(authorization.Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(
            pk=bundle.request.user.pk
        )

    def read_detail(self, object_list, bundle):
        return bundle.obj == bundle.request.user


class TaskStoreAuthorization(authorization.Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(
            store__user=bundle.request.user
        )

    def read_detail(self, object_list, bundle):
        return bundle.obj.store.user == bundle.request.user
