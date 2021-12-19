from __future__ import annotations

import json
import logging
from typing import Optional, List, TYPE_CHECKING
from typing_extensions import TypedDict

import oauthlib.oauth1
import requests
from urllib.parse import parse_qs, urlencode

from django.conf import settings
from django.urls import reverse

from .lock import get_lock_redis

if TYPE_CHECKING:
    from inthe_am.taskmanager.models.taskstore import TaskStore


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
        f"{user.username}.trello_auth",
        600,
        json.dumps(request_token),
    )

    params = {
        "oauth_token": request_token[0],
        "name": APP_NAME,
        "expiration": "never",
        "scope": "read,write",
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"


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

    url = "{}?{}".format(
        SUBSCRIPTION_URL.format(user_token=user_token),
        urlencode(
            {
                "key": settings.TRELLO_API_KEY,
            }
        ),
    )
    data = {
        "description": f"Send task updates for {object_id} to Inthe.AM",
        "callbackURL": callback_url,
        "idModel": object_id,
    }
    result = requests.post(url, data)

    if result.status_code != 200:
        raise RuntimeError(result.content)

    return True


class WebhookDefinition(TypedDict):
    id: str
    description: str
    idModel: str
    callbackURL: str
    active: bool
    consecutiveFailures: int
    firstConsecutiveFailDate: Optional[str]


def get_all_client_webhooks(store: TaskStore) -> List[WebhookDefinition]:
    return store.trello_board.client_request(
        "GET",
        f"/1/tokens/{store.trello_board.client._token}/webhooks",
    ).json()


def delete_webhook_by_id(store: TaskStore, hook_id: str) -> bool:
    return store.trello_board.client_request("DELETE", f"/1/webhooks/{hook_id}").ok
