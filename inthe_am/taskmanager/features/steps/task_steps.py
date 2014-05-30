import datetime
import json
import re
from urlparse import urljoin

from behave import given, when, then, step
import pytz

from django.conf import settings

from inthe_am.taskmanager.models import TaskStore


def get_store():
    return TaskStore.objects.get(user__email=settings.TESTING_LOGIN_USER)


def get_json_value(value):
    if re.match(r'^\d{8}T\d{6}Z$', value):
        return datetime.datetime.strptime(
            value,
            '%Y%m%dT%H%M%SZ'
        ).replace(tzinfo=pytz.UTC)
    return json.loads(value)


@then(u'a task with the {field} "{value}" will exist')
def task_with_field_exists(context, field, value):
    store = get_store()
    matches = store.client.filter_tasks({
        field: value
    })
    assert len(matches) > 0, "No task found with %s == %s" % (
        field, value
    )


@then(u'a single {status} task with the following details will exist')
def task_with_details(context, status):
    store = get_store()
    tasks = store.client.filter_tasks({'status': status})
    assert len(tasks) == 1, "Asserted single task to be found, found %s" % (
        len(tasks)
    )
    task = tasks[0]
    for key, value in context.table.rows:
        assert task[key] == get_json_value(value), (
            "Task field %s's value is %s, not %s" % (
                key,
                task[key],
                value,
            )
        )


@then(u'a single {status} task will have its "{field}" field set')
def task_non_null_field(context, status, field):
    store = get_store()
    tasks = store.client.filter_tasks({'status': status})
    assert len(tasks) == 1, "Asserted single task to be found, found %s" % (
        len(tasks)
    )
    task = tasks[0]
    assert task.get(field)


@then(u'a single {status} task will not have its "{field}" field set')
def task_null_field(context, status, field):
    store = get_store()
    tasks = store.client.filter_tasks({'status': status})
    assert len(tasks) == 1, "Asserted single task to be found, found %s" % (
        len(tasks)
    )
    task = tasks[0]
    assert not task.get(field)


@given(u'a task with the {field} "{value}" exists')
def task_existing_with_value(context, field, value):
    store = get_store()
    basic_task = {
        'description': 'Gather at Terminus for Hari Seldon\'s Address',
        'project': 'terminus_empire',
        'tags': ['next_steps', 'mule'],
    }
    if field == 'tags':
        value = value.split(',')
    basic_task[field] = value
    task = store.client.task_add(**basic_task)
    context.created_task_id = task['uuid']


@then(u'a task named "{value}" is visible in the task list')
def task_with_description_visible(context, value):
    context.execute_steps(u'''
        then the element at CSS selector "{selector}" has text "{value}"
    '''.format(
        selector='div.task-list-item p.description',
        value=value
    ))


@then(u'a task named "{value}" is the opened task')
def task_with_description_visible_main(context, value):
    context.execute_steps(u'''
        then the element at CSS selector "{selector}" has text "{value}"
    '''.format(
        selector='h1.title',
        value=value
    ))


@when(u'the user creates a new task with the description "{value}"')
def task_with_new_description(context, value):
    context.execute_steps(u'''
        When the user clicks the link "New"
        And the user waits for 1 seconds
        And the user enters the text "{val}" into the field named "description"
        And the user clicks the button labeled "Save"
        And the user waits for 1 seconds
    '''.format(
        val=value
    ))


@given(u'the user is viewing an existing task with the {field} "{value}"')
def logged_in_and_viewing_task(context, field, value):
    context.execute_steps(u'''
        Given the user is logged-in
        And a task with the {field} "{value}" exists
        And the user goes to the task's URL
    '''.format(
        field=field,
        value=value,
    ))


@step(u'the user goes to the task\'s URL')
def user_goes_to_tasks_url(context):
    url = urljoin(
        context.config.server_url, '/tasks/%s' % context.created_task_id
    )
    context.browser.visit(url)


@given(u'a task with the following details exists')
def existing_task_with_details(context):
    task = {
        'description': 'Untitled'
    }
    for key, value in context.table.rows:
        task[key] = get_json_value(value)

    store = get_store()
    description = task.pop('description')
    task = store.client.task_add(description, **task)
    context.created_task_id = task['uuid']


@then(u"the following values are visible in the task's details")
def following_values_visible_details(context):
    visible_data = {}
    for row in context.browser.find_by_xpath("//table[@class='details']//tr"):
        key = row.find_by_tag('th')[0].text
        value = row.find_by_tag('td')[0].text
        visible_data[key] = value

    for key, value in context.table.rows:
        actual_value = visible_data.get(key, None)
        assert actual_value == value, "%s != %s" % (
            actual_value,
            value,
        )
