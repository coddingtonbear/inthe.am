import datetime
import json
import re
import time

from behave import given, when, then, step
import pytz

from inthe_am.taskmanager.merge_tasks import (
    find_all_duplicate_tasks, find_duplicate_tasks, merge_tasks
)

from utils import get_store


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
        assert task.get(key) == get_json_value(value), (
            "Task field %s's value is %s, not %s" % (
                key,
                task.get(key),
                value,
            )
        )


@given(u'the user\'s task store is configured with the following options')
def store_configuration(context):
    store = get_store()
    for key, value in context.table.rows:
        setattr(store, key, get_json_value(value))
    store.save()


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
    context.execute_steps(u'''
        then the user accesses the url "%s"
    ''' % (
        '/tasks/%s' % context.created_task_id
    ))


@step(u'the user clicks the refresh button')
def user_clicks_refresh(context):
    context.browser.find_by_id('refresh-link').first.find_by_tag('a').click()
    time.sleep(1)


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
    context.execute_steps(u'''
        then the user clicks the refresh button
    ''')


@then(u'{count} {status} tasks exist in the user\'s task list')
def task_count_matches(context, count, status):
    count = int(count)

    store = get_store()
    tasks = store.client.filter_tasks({'status': status})

    assert len(tasks) == count


@then(u"the following values are visible in the task's details")
def following_values_visible_details(context):
    visible_data = {}
    for row in context.browser.find_by_xpath("//table[@class='details']//tr"):
        key = row.find_by_tag('th')[0].text.lower()
        value = row.find_by_tag('td')[0].text
        visible_data[key] = value

    for key, value in context.table.rows:
        actual_value = visible_data.get(key.lower(), None)
        assert actual_value == value, "%s != %s" % (
            actual_value,
            value,
        )


@given(u'a task "{name}" with the following details')
def task_with_following_details(context, name):
    store = get_store()
    task = store.client.task_add(
        **{row[0]: get_json_value(row[1]) for row in context.table.rows}
    )

    if not hasattr(context, 'named_tasks'):
        context.named_tasks = {}

    context.named_tasks[name] = task


@when(u'the tasks "{left}" and "{right}" are merged')
def named_tasks_merged(context, left, right):
    alpha = context.named_tasks[left]
    beta = context.named_tasks[right]

    alpha, beta = merge_tasks(alpha, beta)

    context.named_tasks[left] = alpha
    context.named_tasks[right] = beta


@then(u'the task "{left}" will be annotated as a duplicate of "{right}"')
def task_annotated_as_duplicate(context, left, right):
    beta = context.named_tasks[left]
    alpha = context.named_tasks[right]

    assert alpha['intheammergedfrom'] == str(beta['uuid']), (
        "No backreference set."
    )
    assert beta['intheamduplicateof'] == str(alpha['uuid']), (
        "Not marked as duplicate."
    )

    context.named_tasks[left] = beta
    context.named_tasks[right] = alpha


@when(u'I search for duplicate tasks')
def when_search_for_duplicate_tasks(context):
    store = get_store()

    context.duplicates_found = find_all_duplicate_tasks(store)


@then(u'task "{left}" and task "{right}" are found as duplicates')
def tasks_are_found_as_duplicates(context, left, right):
    alpha = context.named_tasks[left]
    beta = context.named_tasks[right]

    to_find = {alpha['uuid'], beta['uuid']}
    assert to_find in context.duplicates_found, (
        "Tasks were not found in duplicates: %s" % context.duplicates_found
    )


@when(u'I search for duplicates of task "{name}"')
def task_search_for_duplicates_of(context, name):
    store = get_store()
    task = context.named_tasks[name]

    context.duplicate_found = find_duplicate_tasks(store, task)


@then(
    u'the task I searched for duplicates of is found to be a '
    u'duplicate of "{name}"'
)
def task_found_to_be_duplicate_of(context, name):
    task = context.named_tasks[name]

    assert context.duplicate_found == {task['uuid']}, (
        "Appropriate duplicate was not found: %s" % context.duplicate_found
    )
