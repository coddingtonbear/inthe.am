from contextlib import contextmanager


@contextmanager
def git_checkpoint(store, message, function=None, args=None, kwargs=None):
    store.create_git_checkpoint(
        message,
        function=function,
        args=args,
        kwargs=kwargs,
        pre_operation=True
    )
    yield
    store.create_git_checkpoint(
        message,
        function=function,
        args=args,
        kwargs=kwargs
    )
