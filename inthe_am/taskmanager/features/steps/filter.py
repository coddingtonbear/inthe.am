import time

from behave import then, when


def get_tasks_from_sidebar(context):
    tasks = []

    all_tasks = context.browser.find_by_css('#list .task')
    for task in all_tasks:
        tasks.append(task.find_by_css('.description').value)

    return tasks


@when(u'the filter "{value}" is supplied')
def supply_filter(context, value):
    context.browser.find_by_id("filter-string").type(value)
    time.sleep(1)


@then(u'a task with the description "{description}" is visible in the sidebar')
def task_is_visible_in_sidebar(context, description):
    tasks = get_tasks_from_sidebar(context)
    assert description in tasks, tasks


@then(
    u'a task with the description "{description}" '
    u'is not visible in the sidebar'
)
def task_is_not_visible_in_sidebar(context, description):
    tasks = get_tasks_from_sidebar(context)
    assert description not in tasks, tasks
