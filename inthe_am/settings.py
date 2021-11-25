"""
Django settings for inthe.am project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import json
import os
from subprocess import check_output
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TRAVIS = True if os.environ.get("TRAVIS") else False
TESTING = ("test" in sys.argv) or TRAVIS

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get("DJANGO_DEBUG", False)))

RUN_LOCALLY = {
    "python_path": "python3",
    "runserver_port": 8001,
    "ember_path": f"{BASE_DIR}/node_modules/.bin/ember",
    "ember_port": 8009,
}

CA_CERT_PATH = "/tmp/ca.crt"

DOMAIN_NAME = os.environ.get("DOMAIN_NAME", "localhost")

# Nginx is the only route to reach this, and it will be
ALLOWED_HOSTS = [DOMAIN_NAME]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": True,
        },
    },
]

AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

DEFAULT_LOGIN_ROUTE = ""

GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {"access_type": "offline"}

ROOT_URLCONF = "inthe_am.urls"

WSGI_APPLICATION = "inthe_am.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

CONN_MAX_AGE = None

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = "/static/"

ENVIRONMENT_SETTING_PREFIX = "TWWEB_"

LOGIN_REDIRECT_URL = "/"

TASK_STORAGE_PATH = os.environ.get(
    "TASK_STORAGE_PATH", os.path.join(BASE_DIR, "task_data")
)

GITTER_WEBHOOK_URL = os.environ.get("GITTER_WEBHOOK_URL", "")

STATIC_ROOT = os.environ.get("STATIC_ROOT", os.path.join(BASE_DIR, "static"))

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "memcached:11211",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

STATUS_OFFLOAD_SOCKET = os.environ.get("STATUS_OFFLOAD_SOCKET", None)

TOS_VERSION = 1
PRIVACY_POLICY_VERSION = 1

RAVEN_DSN = os.environ.get("RAVEN_DSN", "")
DATABASE_ENGINE = "django.db.backends.postgresql_psycopg2"
DATABASE_NAME = os.environ["DB_NAME"]
DATABASE_USER = os.environ["DB_USER"]
DATABASE_PASSWORD = os.environ["DB_PASS"]
DATABASE_HOST = os.environ["DB_SERVICE"]
DATABASE_PORT = os.environ["DB_PORT"]

EVENT_STREAM_TIMEOUT = 3600
EVENT_STREAM_LOOP_INTERVAL = 1
EVENT_STREAM_HEARTBEAT_INTERVAL = 15

LOCKFILE_TIMEOUT_SECONDS = 300
LOCKFILE_WAIT_TIMEOUT = 10
LOCKFILE_CHECK_INTERVAL = 0.5

SYNC_LISTENER_WARNING_TIMEOUT = 600

TEST_RUNNER = "django_behave.runner.DjangoBehaveTestSuiteRunner"
TEST_ALWAYS_SAVE_FULL_PAGE_DETAILS = False

BROKER_URL = "redis://redis:6379/1"
CELERYD_CONCURRENCY = 10
CELERY_HIJACK_ROOT_LOGGER = False

REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 2

SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "no-reply@localhost")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@localhost")
DJANGO_MAILBOX_STORE_ORIGINAL_MESSAGE = True

# Relay support/privacy messages to the appropriate inboxes
MAIL_FORWARDING = json.loads(os.environ.get("MAIL_FORWARDING", json.dumps({})))

TASKWARRIOR_CONFIG_OVERRIDES = {
    "gc": "off",
    "recurrence": {
        "confirmation": "no",
    },
    "uda": {
        "intheamattachments": {
            "type": "string",
            "label": "Inthe.AM Attachments",
        },
        "intheamoriginalemailsubject": {
            "type": "string",
            "label": "Inthe.AM E-mail Subject",
        },
        "intheamoriginalemailid": {
            "type": "numeric",
            "label": "Inthe.AM E-mail ID",
        },
        "intheamtrelloid": {
            "type": "string",
            "label": "Inthe.AM Trello Object ID",
        },
        "intheamtrelloboardid": {
            "type": "string",
            "label": "Inthe.AM Trello Board ID",
        },
        "intheamtrellolistid": {
            "type": "string",
            "label": "Inthe.AM Trello List ID",
        },
        "intheamtrellolistname": {
            "type": "string",
            "label": "Inthe.AM Trello List Name",
        },
        "intheamtrellourl": {
            "type": "string",
            "label": "Inthe.AM Trello URL",
        },
        "intheamtrellodescription": {
            "type": "string",
            "label": "Inthe.AM Trello Description",
        },
        "intheamtrellolastupdated": {
            "type": "string",
            "label": "Inthe.AM Trello Last Updated",
        },
        "intheamduplicateof": {
            "type": "string",
            "label": "Inthe.AM Duplicate of Task",
        },
        "intheammergedfrom": {
            "type": "string",
            "label": "Inthe.AM Duplicate Tasks Merged",
        },
    },
}

if os.path.exists(os.path.join(BASE_DIR, ".git")):
    VERSION = (
        check_output(
            [
                "git",
                f"--work-tree={BASE_DIR}",
                f"--git-dir={os.path.join(BASE_DIR, '.git')}",
                "rev-parse",
                "HEAD",
            ]
        )
        .strip()
        .decode("utf-8")
    )
else:
    VERSION = "development"

if TESTING:
    CELERY_ALWAYS_EAGER = True

FILE_UPLOAD_MAXIMUM_BYTES = 5 * 2 ** 20
AWS_QUERYSTRING_AUTH = False
DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"

TASK_BINARY = "/usr/local/bin/task"
TASKD_SERVER = os.environ.get("TASKD_SERVER", "taskd:53589")
TASKD_ORG = os.environ.get("TASKD_ORG", "inthe_am")
TASKD_HTTP = os.environ.get("TASKD_HTTP", "taskd:8000")

TESTING_LOGIN_USER = "im_a"
TESTING_LOGIN_PASSWORD = "robot"

TRELLO_SUBSCRIPTION_DOMAIN = f"https://${DOMAIN_NAME}"
TRELLO_UPDATE_MARGIN_SECONDS = 15

ANNOUNCEMENTS_CHANNEL = "__general__"

# Streaming ticket updates enabled?
STREAMING_UPDATES_ENABLED = not DEBUG

if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r"^/api/.*$"

SOCIAL_AUTH_SESSION_EXPIRATION = False
SOCIAL_AUTH_URLOPEN_TIMEOUT = os.environ.get("SOCIAL_AUTH_URLOPEN_TIMEOUT", 30)
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", ""
)

AWS_DEFAULT_ACL = None
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.environ.get(
    "AWS_STORAGE_BUCKET_NAME", "intheam-attachments"
)

INCOMING_TASK_MAILBOX_NAME = "Incoming Tasks"
INCOMING_TASK_MAIL_HOSTNAME = "0.0.0.0"
INCOMING_TASK_MAIL_PORT = 8025

EMAIL_USE_TLS = True
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))

TRELLO_API_KEY = os.environ.get("TRELLO_API_KEY", "")
TRELLO_API_SECRET = os.environ.get("TRELLO_API_SECRET", "")
TRELLO_BOARD_DEFAULT_NAME = os.environ.get(
    "TRELLO_BOARD_DEFAULT_NAME", "Inthe.AM Tasks"
)

LOG_DIR = os.environ.get("LOG_DIR", os.path.join(BASE_DIR, "logs"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": (
                "%(levelname)s:%(name)s:%(asctime)s %(module)s %(process)d "
                "%(thread)d %(message)s"
            )
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "sentry": {
            "level": "ERROR",
            "class": (
                "raven.contrib.django.handlers.SentryHandler"
                if RAVEN_DSN
                else "logging.NullHandler"
            ),
        },
        "syslog": {
            "level": "INFO",
            "class": "logging.handlers.SysLogHandler",
            "facility": "local7",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {
            "handlers": ["sentry", "syslog", "console"],
            "propagate": True,
            "level": "INFO",
        },
        "django": {
            "handlers": ["null"],
            "propagate": True,
            "level": "INFO",
        },
        "selenium": {"handlers": ["null"], "level": "INFO", "propagate": True},
    },
}

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "social_django",
    "inthe_am.taskmanager.apps.TaskmanagerConfig",
    "django_mailbox",
    "rest_framework",
    "rest_framework.authtoken",
    "django_behave",
    "storages",
]


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",
        "rest_framework.authtoken",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "EXCEPTION_HANDLER": "inthe_am.taskmanager.views.rest_exception_handler",
    "DEFAULT_PAGINATION_CLASS": (
        "inthe_am.taskmanager.pagination.HeaderLimitOffsetPagination"
    ),
}

RAVEN_CONFIG = {
    "dsn": RAVEN_DSN,
}

if RAVEN_DSN:
    INSTALLED_APPS.append(
        "raven.contrib.django.raven_compat",
    )

DATABASES = {
    "default": {
        "ENGINE": DATABASE_ENGINE,
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
        "HOST": DATABASE_HOST,
        "PORT": DATABASE_PORT,
        "CONN_MAX_AGE": 30,
    }
}
