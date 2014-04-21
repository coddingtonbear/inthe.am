import os
import string
import time
from urlparse import urljoin

from django.conf import settings

from splinter.browser import Browser

from inthe_am.taskmanager import models


TEST_COUNTERS = {
    'following': {},
    'before': {}
}


def sanitize_name(name):
    acceptable_letters = []
    for char in name:
        if char in string.letters:
            acceptable_letters.append(char)
        if char == ' ':
            acceptable_letters.append('_')
    return ''.join(acceptable_letters)


def save_page_details(context, step, prefix):
    global TEST_COUNTERS

    scenario_name = sanitize_name(context.scenario.name)
    step_name = sanitize_name(step.name)

    status = 'FAIL' if context.failed else 'OK'

    if scenario_name not in TEST_COUNTERS[prefix]:
        TEST_COUNTERS[prefix][scenario_name] = 0
    TEST_COUNTERS[prefix][scenario_name] += 1

    name = '{scenario}_{num}_{step}_{prefix}_{status}'.format(
        scenario=scenario_name,
        num=TEST_COUNTERS[prefix][scenario_name],
        step=step_name,
        prefix=prefix,
        status=status,
    )

    context.browser.screenshot(name)
    with open(os.path.join('/tmp', name + '.html'), 'w') as out:
        out.write(context.browser.html.encode('utf-8'))


def before_all(context):
    engine = 'phantomjs'
    context.browser = Browser(engine)
    context.browser.driver.set_window_size(1024, 768)
    context.browser.driver.implicitly_wait(10)
    context.browser.driver.set_page_load_timeout(60)


def after_all(context):
    context.browser.quit()
    context.browser = None


def before_step(context, step):
    if 'TRAVIS' in os.environ:
        save_page_details(context, step, 'before')


def after_step(context, step):
    if 'TRAVIS' in os.environ:
        save_page_details(context, step, 'following')


def before_scenario(context, step):
    models.User.objects.filter(
        email=settings.TESTING_LOGIN_USER
    ).delete()


def after_scenario(context, step):
    context.browser.visit(urljoin(context.config.server_url, '/logout/'))
