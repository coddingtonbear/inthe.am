from behave import given

from .task_steps import get_store


@given('the user has the following custom configuration')
def set_custom_configuration(context):
    store = get_store()
    store.taskrc_extras = context.text
    store.apply_extras()
    store.save()
