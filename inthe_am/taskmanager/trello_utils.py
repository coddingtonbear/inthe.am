import json
import logging

import oauthlib.oauth1
import requests
import urllib
from urllib.parse import parse_qs, urlencode

from django.conf import settings
from django.urls import reverse

from .lock import get_lock_redis


logger = logging.getLogger(__name__)


REQUEST_URL = "https://trello.com/1/OAuthGetRequestToken"
ACCESS_URL = "https://trello.com/1/OAuthGetAccessToken"
AUTHORIZE_URL = "https://trello.com/1/OAuthAuthorizeToken"
SUBSCRIPTION_URL = "https://trello.com/1/tokens/{user_token}/webhooks/"
APP_NAME = "Inthe.AM"


def get_oauth_client(request=None, api_key=None, **params):
    base_params = {
        "client_secret": settings.TRELLO_API_SECRET,
    }
    if request:
        base_params["callback_uri"] = (
            request.build_absolute_uri(reverse("api:task-trello_callback"))
            + "?api_key="
            + api_key
        )

    base_params.update(params)

    return oauthlib.oauth1.Client(settings.TRELLO_API_KEY, **base_params)


def get_request_token(request, api_key):
    client = get_oauth_client(request, api_key)

    uri, headers, body = client.sign(REQUEST_URL)
    response = requests.get(uri, headers=headers)

    request_token = parse_qs(response.content)
    return (
        request_token[b"oauth_token"][0].decode("utf-8"),
        request_token[b"oauth_token_secret"][0].decode("utf-8"),
    )


def get_authorize_url(request, api_key, user):
    request_token = get_request_token(request, api_key)

    client = get_lock_redis()
    client.setex(
        "%s.trello_auth" % user.username, 600, json.dumps(request_token),
    )

    params = {
        "oauth_token": request_token[0],
        "name": APP_NAME,
        "expiration": "never",
        "scope": "read,write",
    }
    return u"{url}?{params}".format(url=AUTHORIZE_URL, params=urlencode(params))


def get_access_token(request, api_key, request_token):
    client = get_oauth_client(
        request,
        api_key=api_key,
        resource_owner_key=request_token[0],
        resource_owner_secret=request_token[1],
        verifier=request.GET["oauth_verifier"],
    )

    uri, headers, body = client.sign(ACCESS_URL)

    response = requests.get(uri, headers=headers)
    access_token = parse_qs(response.content)

    return (
        access_token[b"oauth_token"][0],
        access_token[b"oauth_token_secret"][0],
    )


def subscribe_to_updates(object_id, user_token, callback_url):
    # This kind of sucks, but we'll be creating new objects from
    # a bunch of places, and I really don't want to have to put
    # the request object in thread locals for calculating this properly.
    callback_url = settings.TRELLO_SUBSCRIPTION_DOMAIN + callback_url

    url = "%s?%s" % (
        SUBSCRIPTION_URL.format(user_token=user_token),
        urlencode({"key": settings.TRELLO_API_KEY,}),
    )
    data = {
        "description": "Send task updates for {id} to Inthe.AM".format(id=object_id,),
        "callbackURL": callback_url,
        "idModel": object_id,
    }
    result = requests.post(url, data)

    if result.status_code != 200:
        raise RuntimeError(result.content)

    return True
