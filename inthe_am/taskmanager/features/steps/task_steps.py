from django.conf import settings

from behave import given, when, then, step

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
