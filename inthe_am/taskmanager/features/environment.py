from __future__ import print_function

from collections import Counter
import os
import string
import urllib
from urlparse import urljoin

from django.conf import settings
from django.contrib.auth.models import User
from splinter.browser import Browser


TEST_COUNTERS = {"following": Counter(), "before": Counter(), "demand": Counter()}
ABSOLUTE_COUNTER = 0


def sanitize_name(name):
    acceptable_letters = []
    for char in name:
        if char in string.letters:
            acceptable_letters.append(char)
        if char == " ":
            acceptable_letters.append("_")
    return "".join(acceptable_letters)


def calculate_absolute_path(context, url):
    server_url = context.config.server_url

    if "://" in url:
        return url
    elif url.startswith("/"):
        return server_url + url.lstrip("/")

    return server_url + url


def get_browser(engine, time_zone):
    engine_kwargs = {}
    if engine == "remote" and os.environ.get("TRAVIS"):
        engine_kwargs.update(
            {
                "build": os.environ.get("TRAVIS_BUILD_NUMBER", "dev"),
                "tags": ["CI",],
                "tunnelIdentifier": os.environ.get("TRAVIS_JOB_NUMBER", "0.0",),
                "browser": "chrome",
                "platform": "Windows 10",
                "version": "60.0",
                "timeZone": time_zone.split("/")[1].replace("_", " "),
                "url": (
                    (
                        "http://{username}:{password}" "@ondemand.saucelabs.com/wd/hub"
                    ).format(
                        username=urllib.quote(os.environ["SAUCE_USERNAME"]),
                        password=urllib.quote(os.environ["SAUCE_ACCESS_KEY"]),
                    )
                ),
            }
        )

    browser = Browser(engine, **engine_kwargs)
    browser.driver.set_window_size(1024, 800)
    browser.driver.implicitly_wait(10)
    browser.driver.set_page_load_timeout(60)

    return browser


def before_all(context):
    context.engine = getattr(settings, "WEBDRIVER_BROWSER", "phantomjs")
    context.time_zone = "America/Los_Angeles"
    context.browser = get_browser(context.engine, context.time_zone)
    # Ember is running on :8000, and it knows to send API traffic to :8001
    # where this server is running.
    context.config.server_url = "http://localhost:8000/"
    context.browser.visit(context.config.server_url)
    context.browser.execute_script(
        u"window.localStorage.setItem('disable_ticket_stream', 'yes');"
    )


def after_all(context):
    context.browser.quit()
    context.browser = None


def before_step(context, step):
    pass


def after_step(context, step):
    pass


def before_scenario(context, step):
    if hasattr(settings, "TESTING_LOGIN_USER"):
        User.objects.filter(email=settings.TESTING_LOGIN_USER).delete()


def after_scenario(context, step):
    if hasattr(context, "teardown_steps"):
        for teardown_function in context.teardown_steps:
            teardown_function(context)
        context.teardown_steps = []

    context.browser.visit(urljoin(context.config.server_url, "/logout/"))
