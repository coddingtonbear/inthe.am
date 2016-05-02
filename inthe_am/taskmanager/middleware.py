from inthe_am.taskmanager.models import TaskStore


class AuthenticationTokenMiddleware(object):
    def process_response(self, request, response):
        if request.user.is_authenticated():
            store = TaskStore.get_for_user(request.user)
            response.set_cookie('authentication_token', store.api_key.key)
        else:
            response.set_cookie('authentication_token', '')

        return response
