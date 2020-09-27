import datetime
import json
import time

from behave import given, when, then, step
import ipdb

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.timezone import now

from inthe_am.taskmanager.models import TaskStore, UserMetadata
from inthe_am.taskmanager.debug_utils import artificial_login

from .utils import find_element_and_do, get_user, monkey_patch_browser


@step('the user accesses the url "{url}"')
def user_accesses_the_url(context, url):
    if url != "/":
        full_url = f"{context.config.server_url}#{url}"
    else:
        full_url = context.config.server_url
    context.browser.visit(full_url)
    monkey_patch_browser(context)


@given("the user is logged-in")
def user_is_logged_in(context):
    context.execute_steps(
        """
        when the user accesses the url "/"
    """
    )

    u = get_user()
    store = TaskStore.get_for_user(u)
    if not store.configured:
        store.autoconfigure_taskd()
    context.store = store

    meta = UserMetadata.get_for_user(u)
    meta.tos_version = settings.TOS_VERSION
    meta.tos_accepted = now()
    meta.save()

    context.browser.cookies.add({"authentication_token": store.api_key.key})

    context.execute_steps(
        """
        when the user accesses the url "/"
        then the page contains the heading "Let's get started"
    """
    )


@step("the user accepts the terms and conditions")
def user_accepts_terms_and_conditions(context):
    time.sleep(1)
    page_h2 = context.browser.find_by_tag("h2")
    if page_h2.first.text == "Terms and Conditions of Use of Inthe.AM":
        context.browser.find_by_id("accept-terms").first.click()


@given("the test account user does not exist")
def test_account_user_does_not_exist(context):
    count = User.objects.filter(email=settings.TESTING_LOGIN_USER).count()
    assert count == 0, "Test account user does appear to exist."


@step("the user waits for {num} seconds")
def wait_for_a_bit(context, num):
    time.sleep(int(num))


@when('the user clicks the link "{anchor_text}"')
def clicks_link(context, anchor_text):
    result = find_element_and_do(
        context.browser.find_link_by_partial_text, args=(anchor_text,)
    )
    if not result:
        assert False, f"No links having the text {anchor_text} are clickable."


@when('the user clicks the link with the class "{class_name}"')
def clicks_link_class(context, class_name):
    result = find_element_and_do(context.browser.find_by_css, args=(f".{class_name}",))
    if not result:
        assert False, f"No links having the class {class_name} are clickable."


@when('the user enters the text "{text}" into the field named "{field}"')
def user_enters_text_into_field(context, text, field):
    field = context.browser.find_by_name(field)
    field.click()
    field.type(text)

    # Unfocus the element
    field.type("\t")


@when('the user clears the text field named "{field_name}"')
def user_clears_text_field(context, field_name):
    field = context.browser.find_by_name(field_name)[0]
    field.value = ""


@when('the user selects the option "{text}" from the field named "{field}"')
def user_selects_option_from_field(context, text, field):
    context.browser.find_by_name(field).select(text)


@when('the user clicks the button labeled "{label}"')
def user_clicks_button_labeled(context, label):
    result = find_element_and_do(
        context.browser.find_by_tag,
        args=("button",),
        test=lambda x: x.visible and x.text == label,
    )
    if not result:
        assert False, f"No button with label {label} could be clicked"


@when("the user enters his credentials if necessary")
def user_enters_credentials(context):
    login_form = context.browser.find_by_id("Email")
    if login_form:
        context.browser.find_by_id("Email").type(settings.TESTING_LOGIN_USER)
        context.browser.find_by_id("next").first.click()
        context.browser.find_by_id("Passwd").type(settings.TESTING_LOGIN_PASSWORD)
        context.browser.find_by_id("signIn").first.click()
    time.sleep(1)


@when("the user accepts offline access if necessary")
def accept_offline_access(context):
    needs_approval = context.browser.find_by_id("submit_approve_access")
    if needs_approval:
        time.sleep(1)
        needs_approval.first.click()
    time.sleep(1)


@then("a new account will be created using the test e-mail address")
def testing_account_created(context):
    count = User.objects.filter(email=settings.TESTING_LOGIN_USER).count()
    assert count == 1, "Test account user does not exist."


@step('the page contains the heading "{heading}"')
def page_contains_heading(context, heading):
    all_headings = []
    for tag in ["h1", "h2", "h3"]:
        these_headings = [e.text for e in context.browser.find_by_tag(tag)]
        if heading in these_headings:
            return
        all_headings.extend(these_headings)
    assert False, f"Page should contain '{heading}', has '{all_headings}'"


@then('the element at CSS selector "{selector}" has text "{text}"')
def element_at_selector_has_value(context, selector, text):
    actual = context.browser.find_by_css(selector).text
    assert actual == text, f"{selector}'s value is '{actual}' not '{text}'"


@step("debugger")
def launch_debugger(context):
    ipdb.set_trace()


@step("save page details")
def save_page_details(context):
    from ..environment import save_page_details

    save_page_details(context)


@step("save a screenshot")
@step('save a screenshot as "{name}"')
def save_a_screenshot(context, name=None):
    if name is None:
        name = f"screenshot_{datetime.datetime.now().isoformat('T')}"
    context.browser.screenshot(name)


@step("save console output")
@step('save console output as "{name}"')
def save_console_output(context, name=None):
    if name is None:
        name = f"console_{datetime.datetime.now().isoformat('T')}"
    result = context.browser.evaluate_script("CONSOLE_LOG")
    with open(f"/tmp/{name}.txt", "w") as out:
        for row in result:
            out.write(" ".join([json.dumps(o) for o in row]) + "\n")


@then('the page will transition to "{url}"')
def watch_for_page_transition(context, url):
    timeout = 30  # seconds
    started = time.time()
    while time.time() < started + timeout:
        if url in context.browser.driver.current_url:
            return True
        time.sleep(1)
    assert False, f"Current URL is {context.browser.driver.current_url}"
