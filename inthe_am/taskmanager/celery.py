from __future__ import absolute_import

from celery import Celery

from inthe_am import celery_settings

app = Celery('inthe_am')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object(celery_settings)
app.autodiscover_tasks(lambda: celery_settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
