import time

from selenium.common.exceptions import (
    StaleElementReferenceException,
)


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
        window.localStorage.setItem('disable_ticket_stream', 'yes');
    """.replace('\n', ' '))
    context.browser.execute_script("""
        window.confirm = function(message) {
            lastConfirmationMessage = message; return true;
        }
    """.replace('\n', ' '))
    context.browser.execute_script("""
        CONSOLE_LOG = [];
    """.replace('\n', ' '))
    context.browser.execute_script("""
        window.console.log = function() {
            CONSOLE_LOG.push(arguments)
        }
    """.replace('\n', ''))
