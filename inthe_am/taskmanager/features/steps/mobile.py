from behave import given


@given('the user is using a mobile device')
def using_mobile_device(context):
    context.browser.driver.set_window_size(320, 700)

    if not hasattr(context, 'teardown_steps'):
        context.teardown_steps = []

    context.teardown_steps.append(
        lambda context: context.browser.driver.set_window_size(1024, 1024)
    )
