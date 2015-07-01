import base64
import hmac
import hashlib
import logging

import oauthlib.oauth1
import requests
import urllib
from urlparse import parse_qs

from django.conf import settings
from django.core.urlresolvers import reverse


logger = logging.getLogger(__name__)


REQUEST_URL = "https://trello.com/1/OAuthGetRequestToken"
ACCESS_URL = "https://trello.com/1/OAuthGetAccessToken"
AUTHORIZE_URL = "https://trello.com/1/OAuthAuthorizeToken"
SUBSCRIPTION_URL = "https://trello.com/1/tokens/{user_token}/webhooks/"
APP_NAME = "Inthe.AM"


def get_oauth_client(request=None, **params):
    base_params = {
        'client_secret': settings.TRELLO_API_SECRET,
    }
    if request:
        base_params['callback_uri'] = request.build_absolute_uri(
            reverse(
                'trello_callback',
                kwargs={
                    'api_name': 'v1',
                    'resource_name': 'task',
                }
            )
        )

    base_params.update(params)

    return oauthlib.oauth1.Client(
        settings.TRELLO_API_KEY,
        **base_params
    )


def get_request_token(request):
    client = get_oauth_client(request)

    uri, headers, body = client.sign(REQUEST_URL)
    response = requests.get(uri, headers=headers)

    request_token = parse_qs(response.content)
    return (
        request_token['oauth_token'][0],
        request_token['oauth_token_secret'][0],
    )


def get_authorize_url(request):
    request_token = get_request_token(request)
    request.session['trello_oauth_token'] = request_token
    params = {
        'oauth_token': request_token[0],
        'name': APP_NAME,
        'expiration': 'never',
        'scope': 'read,write',
    }
    return u'{url}?{params}'.format(
        url=AUTHORIZE_URL,
        params=urllib.urlencode(params)
    )


def get_access_token(request):
    request_token = request.session['trello_oauth_token']

    client = get_oauth_client(
        request,
        resource_owner_key=request_token[0],
        resource_owner_secret=request_token[1],
        verifier=request.GET['oauth_verifier']
    )

    uri, headers, body = client.sign(ACCESS_URL)

    response = requests.get(uri, headers=headers)
    access_token = parse_qs(response.content)

    return (
        access_token['oauth_token'][0],
        access_token['oauth_token_secret'][0],
    )


def subscribe_to_updates(object_id, user_token, callback_url):
    # This kind of sucks, but we'll be creating new objects from
    # a bunch of places, and I really don't want to have to put
    # the request object in thread locals for calculating this properly.
    callback_url = settings.TRELLO_SUBSCRIPTION_DOMAIN + callback_url

    url = "%s?%s" % (
        SUBSCRIPTION_URL.format(user_token=user_token),
        urllib.urlencode({
            'key': settings.TRELLO_API_KEY,
        })
    )
    data = {
        'description': 'Send task updates for {id} to Inthe.AM'.format(
            id=object_id,
        ),
        'callbackURL': callback_url,
        'idModel': object_id,
    }
    result = requests.post(url, data)

    if result.status_code != 200:
        raise RuntimeError(result.content)

    return True


def message_signature_is_valid(request):
    def b64_digest(data):
        return base64.encodestring(
            hmac.new(
                settings.TRELLO_API_SECRET,
                data,
                hashlib.sha1
            ).digest()
        )

    expected_hash = b64_digest(request.META.get('HTTP_X_TRELLO_WEBHOOK'))

    callback_url = request.build_absolute_uri(request.path.encode('utf-8'))
    content = request.body + callback_url

    actual_hash = b64_digest(b64_digest(content))

    if actual_hash != expected_hash:
        logger.warning(
            "Trello hash did not match: %s != %s.",
            actual_hash,
            expected_hash,
            extra={
                'stack': True,
            }
        )
        return False

    return True
