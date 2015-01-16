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
