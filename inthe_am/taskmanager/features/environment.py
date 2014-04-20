import json
import os
from urlparse import urljoin

from django.conf import settings

from splinter.browser import Browser

from inthe_am.taskmanager import models


TEST_COUNTERS = {
    'following': {},
    'before': {}
}


def save_page_details(context, prefix):
    global TEST_COUNTERS
    name = '-'.join([
        context.scenario.name.replace(' ', '_'),
    ])

    status = 'FAIL' if context.failed else 'OK'

    if name not in TEST_COUNTERS[prefix]:
        TEST_COUNTERS[prefix][name] = 0
    TEST_COUNTERS[prefix][name] += 1

    name = name + '_%s_%s_%s_' % (
        TEST_COUNTERS[prefix][name],
        prefix,
        status
    )

    context.browser.screenshot(name)
    with open(os.path.join('/tmp', name + '.html'), 'w') as out:
        out.write(context.browser.html.encode('utf-8'))
    with open(os.path.join('/tmp', name + '.html.errors.log'), 'w') as out:
        try:
            result = context.browser.evaluate_script(
                'JSON.stringify(window.javascript_errors);'
            )
        except Exception as e:
            out.write(str(e))
            result = None
        if result:
            loaded = json.loads(result)
            out.write('%s messages recorded.\n\n' % len(loaded))
            out.write('\n'.join(loaded))


def before_all(context):
    engine = 'phantomjs'
    context.browser = Browser(engine)
    context.browser.driver.set_window_size(1024, 768)
    context.browser.driver.implicitly_wait(30)
    context.browser.driver.set_page_load_timeout(60)


def after_all(context):
    context.browser.quit()
    context.browser = None


def before_step(context, step):
    if 'TRAVIS' in os.environ:
        save_page_details(context, 'before')


def after_step(context, step):
    if 'TRAVIS' in os.environ:
        save_page_details(context, 'following')


def before_scenario(context, step):
    models.User.objects.filter(
        email=settings.TESTING_LOGIN_USER
    ).delete()


def after_scenario(context, step):
    context.browser.visit(urljoin(context.config.server_url, '/logout/'))
