from __future__ import absolute_import

import copy
import logging
import os

from celery import Celery

from django.conf import settings


from inthe_am import settings as isettings
logging_settings = copy.deepcopy(isettings.LOGGING)
for name, details in logging_settings.items():
    if 'filename' in details:
        details['filename'] = "".join([
            os.path.splitext(details['filename'])[0],
            '.celery',
            os.path.splitext(details['filename'])[1]
        ])
logging.config.dictConfig(logging_settings)


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inthe_am.settings')

app = Celery('inthe_am')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
