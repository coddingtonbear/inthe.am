import json

from django.conf import settings

from behave import given, when, then

from inthe_am.taskmanager.models import TaskStore


def get_store():
    return TaskStore.objects.get(user__email=settings.TESTING_LOGIN_USER)


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
        assert task[key] == json.loads(value), (
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


@given(u'an existing task with the {field} "{value}"')
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
        And an existing task with the {field} "{value}"
    '''.format(
        field=field,
        value=value,
    ))
