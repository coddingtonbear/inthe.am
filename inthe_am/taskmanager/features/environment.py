from collections import Counter
import os
import string
from urlparse import urljoin

from django.conf import settings

from splinter.browser import Browser

from inthe_am.taskmanager import models


TEST_COUNTERS = {
    'following': Counter(),
    'before': Counter()
}
ABSOLUTE_COUNTER = 0


def sanitize_name(name):
    acceptable_letters = []
    for char in name:
        if char in string.letters:
            acceptable_letters.append(char)
        if char == ' ':
            acceptable_letters.append('_')
    return ''.join(acceptable_letters)


def save_page_details(context, step, prefix):
    global TEST_COUNTERS, ABSOLUTE_COUNTER
    ABSOLUTE_COUNTER += 1

    this_absolute_counter = ABSOLUTE_COUNTER

    scenario_name = sanitize_name(context.scenario.name)
    step_name = sanitize_name(step.name)

    status = 'FAIL' if context.failed else 'OK'

    TEST_COUNTERS[prefix][scenario_name] += 1
    this_counter = TEST_COUNTERS[prefix][scenario_name]

    name = '{absolute}_{scenario}_{num}_{step}_{prefix}_{status}'.format(
        absolute=str(this_absolute_counter).zfill(5),
        scenario=scenario_name,
        num=str(this_counter).zfill(2),
        step=step_name,
        prefix=prefix,
        status=status,
    )

    context.browser.screenshot(name)
    with open(os.path.join('/tmp', name + '.html'), 'w') as out:
        out.write(context.browser.html.encode('utf-8'))


def before_all(context):
    engine = getattr(settings, 'WEBDRIVER_BROWSER', 'phantomjs')
    context.browser = Browser(engine)
    context.browser.driver.set_window_size(1024, 1024)
    context.browser.driver.implicitly_wait(10)
    context.browser.driver.set_page_load_timeout(60)
    context.browser.visit(context.config.server_url)
    context.browser.execute_script(
        u"window.localStorage.setItem('disable_ticket_stream', 'yes');"
    )


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
