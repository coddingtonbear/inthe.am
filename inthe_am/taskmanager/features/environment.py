import os
from urlparse import urljoin

from django.conf import settings

from splinter.browser import Browser

from inthe_am.taskmanager import models


def before_all(context):
    context.browser = Browser('phantomjs')


def after_all(context):
    context.browser.quit()
    context.browser = None


def before_scenario(context, step):
    models.User.objects.filter(
        email=settings.TESTING_LOGIN_USER
    ).delete()


def after_scenario(context, step):
    context.browser.visit(urljoin(context.config.server_url, '/logout/'))


def after_step(context, step):
    if context.failed:
        name = '-'.join([
            context.scenario.name.replace(' ', '_'),
        ])
        context.browser.screenshot(name)
        with open(os.path.join('/tmp', name + '.html'), 'w') as out:
            out.write(context.browser.html)
