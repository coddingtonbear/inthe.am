from importlib import import_module
from io import BytesIO

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import SimpleCookie

from django.middleware import csrf


def artificial_login(**credentials):
    from django.contrib.auth import authenticate, login

    cookies = SimpleCookie()

    user = authenticate(**credentials)
    engine = import_module(settings.SESSION_ENGINE)

    # Create a fake request that goes through request middleware
    request = WSGIRequest(
        {
            "HTTP_COOKIE": cookies.output(header="", sep=";"),
            "PATH_INFO": "/",
            "REMOTE_ADDR": "127.0.0.1",
            "REQUEST_METHOD": "GET",
            "SCRIPT_NAME": "",
            "SERVER_NAME": "testserver",
            "SERVER_PORT": "80",
            "SERVER_PROTOCOL": "HTTP/1.1",
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "http",
            "wsgi.input": BytesIO(),
            "wsgi.errors": BytesIO(),
            "wsgi.multiprocess": True,
            "wsgi.multithread": False,
            "wsgi.run_once": False,
        }
    )
    request.session = engine.SessionStore()
    login(request, user)

    # Save the session values.
    request.session.save()

    # Set the cookie to represent the session.
    session_cookie = settings.SESSION_COOKIE_NAME
    cookies[session_cookie] = request.session.session_key
    cookie_data = {
        "max-age": None,
        "path": "/",
        "domain": settings.SESSION_COOKIE_DOMAIN,
        "secure": settings.SESSION_COOKIE_SECURE or None,
        "expires": None,
    }
    cookies[session_cookie].update(cookie_data)
    return {
        session_cookie: cookies[session_cookie].value,
        settings.CSRF_COOKIE_NAME: csrf._get_new_csrf_key(),
    }
