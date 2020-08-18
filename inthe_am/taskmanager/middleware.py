from inthe_am.taskmanager.models import TaskStore


class AuthenticationTokenMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if hasattr(request, "user") and request.user.is_authenticated():
            store = TaskStore.get_for_user(request.user)
            response.set_cookie("authentication_token", store.api_key.key)
        else:
            response.delete_cookie("authentication_token")

        return response
