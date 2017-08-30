import time

from django.conf import settings
from django.contrib.auth.models import User
from selenium.common.exceptions import (
    StaleElementReferenceException,
)

from inthe_am.taskmanager.models import TaskStore


def find_element_and_do(
    selector, args=None, kwargs=None,
    test=lambda x: x.visible, action=lambda x: x.click(),
    retries=3, retry_sleep=1, post_sleep=1,
):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    for loop in range(3):
        matches = selector(*args, **kwargs)
        for match in matches:
            try:
                if test(match):
                    action(match)
                    time.sleep(post_sleep)
                    return True
            except StaleElementReferenceException:
                pass
        time.sleep(retry_sleep)

    return False


def monkey_patch_browser(context):
    context.browser.execute_script("""
        window.confirm = function(message) {
            lastConfirmationMessage = message; return true;
        }
    """.replace('\n', ' '))
    context.browser.execute_script("""
        window.CONSOLE_LOG = [];
    """.replace('\n', ' '))
    context.browser.execute_script("""
        window.console.log = function() {
            window.CONSOLE_LOG.push(arguments)
        }
    """.replace('\n', ''))
    context.browser.execute_script("""
        window.JS_ERRORS = [];
    """.replace('\n', ' '))
    context.browser.execute_script("""
        window.onerror = function(errorMessage) {
            window.JS_ERRORS.push(errorMessage)
        }
    """.replace('\n', ''))


def get_user():
    u, _ = User.objects.get_or_create(
        username='integration-test',
        email=settings.TESTING_LOGIN_USER
    )
    u.set_password(settings.TESTING_LOGIN_PASSWORD)
    u.save()

    return u


def get_store():
    u = get_user()
    store = TaskStore.get_for_user(u)
    if not store.configured:
        store.autoconfigure_taskd()

    return store
