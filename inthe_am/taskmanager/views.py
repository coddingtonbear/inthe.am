import time

from django_sse.views import BaseSseView
from django.template.response import TemplateResponse

from .models import TaskStore


class Status(BaseSseView):
    def get_store(self):
        if getattr(self, '_store', None) is None:
            try:
                store = TaskStore.objects.get(user=self.request.user)
                setattr(self, '_store', store)
            except TaskStore.DoesNotExist:
                return None

        return self._store

    def iterator(self):
        store = self.get_store()
        head = store.repository.head()
        while True:
            store = self.get_store()
            new_head = store.repository.head()
            if head != new_head:
                self.sse.add_message("status", self.request.user.username)
                yield
            time.sleep(5)


def home(request):
    return TemplateResponse(
        request,
        'home.html',
        {}
    )
