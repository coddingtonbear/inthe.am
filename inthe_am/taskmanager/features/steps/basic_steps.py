from importlib import import_module
from io import BytesIO
import time
from urlparse import urljoin

from behave import given, when, then, step
import ipdb
from selenium.common.exceptions import (
    StaleElementReferenceException,
)

from django.conf import settings
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.http import SimpleCookie
from django.utils.timezone import now
from django.middleware import csrf

from inthe_am.taskmanager.models import TaskStore, UserMetadata


def login(context, **credentials):
    from django.contrib.auth import authenticate, login

    cookies = SimpleCookie()

    user = authenticate(**credentials)
    engine = import_module(settings.SESSION_ENGINE)

    # Create a fake request that goes through request middleware
    request = WSGIRequest(
        {
            'HTTP_COOKIE': cookies.output(header='', sep=';'),
            'PATH_INFO': str('/'),
            'REMOTE_ADDR': str('127.0.0.1'),
            'REQUEST_METHOD': str('GET'),
            'SCRIPT_NAME': str(''),
            'SERVER_NAME': str('testserver'),
            'SERVER_PORT': str('80'),
            'SERVER_PROTOCOL': str('HTTP/1.1'),
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': str('http'),
            'wsgi.input': BytesIO(),
            'wsgi.errors': BytesIO(),
            'wsgi.multiprocess': True,
            'wsgi.multithread': False,
            'wsgi.run_once': False,
        }
    )
    request.session = engine.SessionStore()
    login(request, user)

    # Save the session values.
    request.session.save()

    # Set the cookie to represent the session.
    session_cookie = settings.SESSION_COOKIE_NAME
    cookies[session_cookie] = request.session.session_key
    cookie_data = {
        'max-age': None,
        'path': '/',
        'domain': settings.SESSION_COOKIE_DOMAIN,
        'secure': settings.SESSION_COOKIE_SECURE or None,
        'expires': None,
    }
    cookies[session_cookie].update(cookie_data)
    context.browser.cookies.add(
        {
            session_cookie: cookies[session_cookie].value,
            settings.CSRF_COOKIE_NAME: csrf._get_new_csrf_key(),
        }
    )


@step(u'the user accesses the url "{url}"')
def user_accesses_the_url(context, url):
    full_url = urljoin(context.config.server_url, url)
    context.browser.visit(full_url)
    context.browser.execute_script(
        u"window.localStorage.setItem('disable_ticket_stream', 'yes');"
    )
    time.sleep(2)


@given(u'the user is logged-in')
def user_is_logged_in(context):
    context.execute_steps(u'''
        when the user accesses the url "/"
    ''')
    u = User.objects.create(
        username='integration-test',
        email=settings.TESTING_LOGIN_USER
    )
    u.set_password(settings.TESTING_LOGIN_PASSWORD)
    u.save()

    store = TaskStore.get_for_user(u)
    if not store.configured:
        store.autoconfigure_taskd()

    meta = UserMetadata.get_for_user(u)
    meta.tos_version = settings.TOS_VERSION
    meta.tos_accepted = now()
    meta.save()

    login(
        context,
        username=u.username,
        password=settings.TESTING_LOGIN_PASSWORD
    )
    context.execute_steps(u'''
        when the user accesses the url "/"
        then the page contains the heading "Let's get started"
    ''')


@step(u'the user accepts the terms and conditions')
def user_accepts_terms_and_conditions(context):
    time.sleep(1)
    page_h2 = context.browser.find_by_tag('h2')
    if page_h2.first.text == "Terms and Conditions of Use of Inthe.AM":
        context.browser.find_by_id("accept-terms").first.click()


@given(u'the test account user does not exist')
def test_account_user_does_not_exist(context):
    count = User.objects.filter(
        email=settings.TESTING_LOGIN_USER
    ).count()
    assert count == 0, "Test account user does appear to exist."


@step(u'the user waits for {num} seconds')
def wait_for_a_bit(context, num):
    time.sleep(int(num))


@when(u'the user clicks the link "{anchor_text}"')
def clicks_link(context, anchor_text):
    matches = context.browser.find_link_by_partial_text(anchor_text)
    for match in matches:
        try:
            if match.visible:
                match.click()
                return
        except StaleElementReferenceException:
            pass
    assert False, "Of %s anchors with text %s, none were clickable." % (
        len(matches),
        anchor_text,
    )


@when(u'the user enters the text "{text}" into the field named "{field}"')
def user_enters_text_into_field(context, text, field):
    context.browser.find_by_name(field).type(text)


@when(u'the user clicks the button labeled "{label}"')
def user_clicks_button_labeled(context, label):
    for button in context.browser.find_by_tag("button"):
        if button.visible and button.text == label:
            button.click()
            return
    assert False, "No button with label %s could be clicked" % label


@when(u'the user enters his credentials if necessary')
def user_enters_credentials(context):
    login_form = context.browser.find_by_id('Email')
    if login_form:
        context.browser.find_by_id('Email').type(
            settings.TESTING_LOGIN_USER
        )
        context.browser.find_by_id('Passwd').type(
            settings.TESTING_LOGIN_PASSWORD
        )
        context.browser.find_by_id('signIn').first.click()

    needs_approval = context.browser.find_by_id('submit_approve_access')
    if needs_approval:
        time.sleep(2)
        needs_approval.first.click()


@then(u'a new account will be created using the test e-mail address')
def testing_account_created(context):
    count = User.objects.filter(
        email=settings.TESTING_LOGIN_USER
    ).count()
    assert count == 1, "Test account user does not exist."


@step(u'the page contains the heading "{heading}"')
def page_contains_heading(context, heading):
    all_headings = []
    for tag in ['h1', 'h2', 'h3']:
        these_headings = [e.text for e in context.browser.find_by_tag(tag)]
        if heading in these_headings:
            return
        all_headings.extend(these_headings)
    assert False, \
        "Page should contain '%s', has '%s'" % (
            heading, all_headings
        )


@then(u'the element at CSS selector "{selector}" has text "{text}"')
def element_at_selector_has_value(context, selector, text):
    actual = context.browser.find_by_css(selector).text
    assert actual == text, "%s's value is '%s' not '%s'" % (
        selector,
        actual,
        text
    )


@step(u'debugger')
def launch_debugger(context):
    ipdb.set_trace()
