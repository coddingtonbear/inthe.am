import os
import time
from urlparse import urljoin

from django.conf import settings

from splinter.browser import Browser

from inthe_am.taskmanager import models


TEST_COUNTERS = {}


def before_all(context):
    if 'TRAVIS' in os.environ:
        engine = 'firefox'
    else:
        engine = 'phantomjs'
    context.browser = Browser(engine)


def after_all(context):
    context.browser.quit()
    context.browser = None


def before_step(context, step):
    if 'TRAVIS' in os.environ:
        time.sleep(5)


def before_scenario(context, step):
    models.User.objects.filter(
        email=settings.TESTING_LOGIN_USER
    ).delete()
    context.browser.driver.set_window_size(1024, 768)


def after_scenario(context, step):
    context.browser.visit(urljoin(context.config.server_url, '/logout/'))


def after_step(context, step):
    global TEST_COUNTERS
    if context.failed:
        name = '-'.join([
            context.scenario.name.replace(' ', '_'),
        ])

        if name not in TEST_COUNTERS:
            TEST_COUNTERS[name] = 0
        TEST_COUNTERS[name] += 1

        name = name + '_%s_' % TEST_COUNTERS[name]

        context.browser.screenshot(name)
        with open(os.path.join('/tmp', name + '.html'), 'w') as out:
            out.write(context.browser.html)
