import os
import time
from urlparse import urljoin

from django.conf import settings

from splinter.browser import Browser

from inthe_am.taskmanager import models


TEST_COUNTERS = {
    'following': {},
    'after': {}
}


def save_screenshot(context, prefix):
    global TEST_COUNTERS
    if 'TRAVIS' in os.environ:
        if context.failed:
            name = '-'.join([
                context.scenario.name.replace(' ', '_'),
            ])

            if name not in TEST_COUNTERS[prefix]:
                TEST_COUNTERS[prefix][name] = 0
            TEST_COUNTERS[prefix][name] += 1

            name = name + '_%s_%s_' % (
                TEST_COUNTERS[prefix][name],
                prefix,
            )

            context.browser.screenshot(name)
            with open(os.path.join('/tmp', name + '.html'), 'w') as out:
                out.write(context.browser.html.encode('utf-8'))


def before_all(context):
    engine = 'phantomjs'
    context.browser = Browser(engine)


def after_all(context):
    context.browser.quit()
    context.browser = None


def before_step(context, step):
    save_screenshot(context, 'before')


def after_step(context, step):
    save_screenshot(context, 'following')


def before_scenario(context, step):
    models.User.objects.filter(
        email=settings.TESTING_LOGIN_USER
    ).delete()
    context.browser.driver.set_window_size(1024, 768)


def after_scenario(context, step):
    context.browser.visit(urljoin(context.config.server_url, '/logout/'))
