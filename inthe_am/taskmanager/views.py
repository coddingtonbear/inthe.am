import time

from django_sse.views import BaseSseView
from django.template.response import TemplateResponse


class Status(BaseSseView):
    def iterator(self):
        while True:
            self.sse.add_message("status", self.request.user.username)
            yield
            time.sleep(1)


def home(request):
    return TemplateResponse(
        request,
        'home.html',
        {}
    )
