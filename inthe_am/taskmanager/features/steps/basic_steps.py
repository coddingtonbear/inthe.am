import time

from behave import given, when, then, step
import ipdb

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.timezone import now

from inthe_am.taskmanager.models import TaskStore, UserMetadata
from inthe_am.taskmanager.debug_utils import artificial_login

from .utils import find_element_and_do


@step(u'the user accesses the url "{url}"')
def user_accesses_the_url(context, url):
    if url != '/':
        full_url = '%s#%s' % (
            context.config.server_url,
            url,
        )
    else:
        full_url = context.config.server_url
    context.browser.visit(full_url)
    context.browser.execute_script(
        u"window.localStorage.setItem('disable_ticket_stream', 'yes');"
    )


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
    context.store = store

    meta = UserMetadata.get_for_user(u)
    meta.tos_version = settings.TOS_VERSION
    meta.tos_accepted = now()
    meta.save()

    cookies = artificial_login(
        username=u.username,
        password=settings.TESTING_LOGIN_PASSWORD
    )
    context.browser.cookies.add(cookies)

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
    result = find_element_and_do(
        context.browser.find_link_by_partial_text,
        args=(anchor_text, )
    )
    if not result:
        assert False, "No links having the text %s are clickable." % (
            anchor_text,
        )


@when(u'the user clicks the link with the class "{class_name}"')
def clicks_link_class(context, class_name):
    result = find_element_and_do(
        context.browser.find_by_css,
        args=(".%s" % class_name, )
    )
    if not result:
        assert False, "No links having the class %s are clickable." % (
            class_name,
        )


@when(u'the user enters the text "{text}" into the field named "{field}"')
def user_enters_text_into_field(context, text, field):
    context.browser.find_by_name(field).type(text)


@when(u'the user clears the text field named "{field_name}"')
def user_clears_text_field(context, field_name):
    field = context.browser.find_by_name(field_name)[0]
    field.value = ''


@when(u'the user selects the option "{text}" from the field named "{field}"')
def user_selects_option_from_field(context, text, field):
    context.browser.find_by_name(field).select(text)


@when(u'the user clicks the button labeled "{label}"')
def user_clicks_button_labeled(context, label):
    for button in context.browser.find_by_tag("button"):
        if button.visible and button.text == label:
            button.click()
            time.sleep(1)
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
        time.sleep(1)
        needs_approval.first.click()
    time.sleep(1)


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


@step(u'confirmation dialogs are disabled')
def disable_confirmation_dialog(context):
    context.browser.execute_script(
        'window.confirm = function(message) '
        '{ lastConfirmationMessage = message; return true; }'
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


@then(u'the page will transition to "{url}"')
def watch_for_page_transition(context, url):
    timeout = 5 * 60  # minutes
    started = time.time()
    while time.time() < started + timeout:
        if url in context.browser.driver.current_url:
            return True
        time.sleep(1)
    assert False, "Current URL is %s" % context.browser.driver.current_url
