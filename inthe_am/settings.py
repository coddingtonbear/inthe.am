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
SECRET_KEY = "nou@d*dme8l60^9mzyk@#ikeobd0ws#p*mj#e*i*g33d#blsc9"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
if os.uname()[1] == "eugene.adamcoddington.net":
    DEBUG = False

RUN_LOCALLY = {
    "python_path": "python",
    "runserver_port": 8001,
    "ember_path": "%s/node_modules/.bin/ember" % BASE_DIR,
    "ember_port": 8009,
}

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [
    "inthe.am",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "inthe_am.taskmanager.middleware.AuthenticationTokenMiddleware",
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
        "DIRS": [
            # insert your TEMPLATE_DIRS here
        ],
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
        },
    },
]

AUTHENTICATION_BACKENDS = (
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

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

TASK_STORAGE_PATH = os.path.join(BASE_DIR, "task_data")

STATIC_ROOT = os.path.join(BASE_DIR, "static")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

SOCIAL_AUTH_SESSION_EXPIRATION = False

TOS_VERSION = 1
PRIVACY_POLICY_VERSION = 1

RAVEN_DSN = ""
DATABASE_ENGINE = "django.db.backends.sqlite3"
DATABASE_NAME = os.path.join(BASE_DIR, "db.sqlite3")
DATABASE_USER = ""
DATABASE_PASSWORD = ""
DATABASE_HOST = ""
DATABASE_PORT = ""

EVENT_STREAM_TIMEOUT = 3600
EVENT_STREAM_LOOP_INTERVAL = 1
EVENT_STREAM_POLLING_INTERVAL = 60
EVENT_STREAM_HEARTBEAT_INTERVAL = 15
LOCKFILE_TIMEOUT_SECONDS = 300
LOCKFILE_WAIT_TIMEOUT = 10
LOCKFILE_CHECK_INTERVAL = 0.5

SYNC_LISTENER_WARNING_TIMEOUT = 600

TEST_RUNNER = "django_behave.runner.DjangoBehaveTestSuiteRunner"
TEST_ALWAYS_SAVE_FULL_PAGE_DETAILS = False

BROKER_URL = "redis://localhost:6379/1"
CELERYD_CONCURRENCY = 10
CELERY_HIJACK_ROOT_LOGGER = False

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 2

SERVER_EMAIL = "no-reply@localhost"
DJANGO_MAILBOX_STORE_ORIGINAL_MESSAGE = True

# Relay support/privacy messages to the appropriate inboxes
MAIL_FORWARDING = {"somebody@somewhere.com": "someotheraddress@somewhereelse.com"}

TASKWARRIOR_CONFIG_OVERRIDES = {
    "gc": "off",
    "recurrence": {"confirmation": "no",},
    "uda": {
        "intheamattachments": {"type": "string", "label": "Inthe.AM Attachments",},
        "intheamoriginalemailsubject": {
            "type": "string",
            "label": "Inthe.AM E-mail Subject",
        },
        "intheamoriginalemailid": {"type": "numeric", "label": "Inthe.AM E-mail ID",},
        "intheamtrelloid": {"type": "string", "label": "Inthe.AM Trello Object ID",},
        "intheamtrelloboardid": {
            "type": "string",
            "label": "Inthe.AM Trello Board ID",
        },
        "intheamtrellolistid": {"type": "string", "label": "Inthe.AM Trello List ID",},
        "intheamtrellolistname": {
            "type": "string",
            "label": "Inthe.AM Trello List Name",
        },
        "intheamtrellourl": {"type": "string", "label": "Inthe.AM Trello URL",},
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
    VERSION = check_output(
        [
            "git",
            "--work-tree=%s" % BASE_DIR,
            "--git-dir=%s" % os.path.join(BASE_DIR, ".git"),
            "rev-parse",
            "HEAD",
        ]
    ).strip()
else:
    VERSION = "development"

if TESTING:
    CELERY_ALWAYS_EAGER = True

FILE_UPLOAD_MAXIMUM_BYTES = 5 * 2 ** 20
AWS_QUERYSTRING_AUTH = False
DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"

TASKD_BINARY = "/usr/local/bin/taskd"
TASK_BINARY = "/usr/local/bin/task"
TASKD_DATA = "/var/taskd"
TASKD_SIGNING_TEMPLATE = "/var/taskd/cert.template"
TASKD_SERVER = "127.0.0.1:53589"
TASKD_ORG = "testing"

TESTING_LOGIN_USER = "im_a"
TESTING_LOGIN_PASSWORD = "robot"

TRELLO_SUBSCRIPTION_DOMAIN = "https://inthe.am"
TRELLO_UPDATE_MARGIN_SECONDS = 15

ANNOUNCEMENTS_CHANNEL = "__general__"

# Streaming ticket updates enabled?
STREAMING_UPDATES_ENABLED = True

if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r"^/api/.*$"

# Must be sourced from environment:
#  SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
#  SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
#  AWS_ACCESS_KEY_ID
#  AWS_SECRET_ACCESS_KEY
#  AWS_STORAGE_BUCKET_NAME
#  TRELLO_API_KEY
#  TRELLO_API_SECRET
ENVIRONMENT_SETTING_SUFFIXES = {
    "__BOOL": lambda x: bool(int(x)),
    "__INT": lambda x: int(x),
    "__JSON": lambda x: json.loads(x),
}
this_module = sys.modules[__name__]
for key, value in os.environ.items():
    if key.startswith(ENVIRONMENT_SETTING_PREFIX):
        for suffix, fn in ENVIRONMENT_SETTING_SUFFIXES.items():
            if key.endswith(suffix):
                value = fn(value)
                key = key[: -len(suffix)]
        setattr(this_module, key[len(ENVIRONMENT_SETTING_PREFIX) :], value)

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
        "null": {"level": "DEBUG", "class": "logging.NullHandler",},
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "exception_log": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/twweb.error.log"),
            "maxBytes": 1048576,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "taskwarrior": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/twweb.taskwarrior.log"),
            "maxBytes": 1048576,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "tasks": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/twweb.tasks.log"),
            "maxBytes": 1048576,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "mgmt": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/twweb.mgmt.log"),
            "maxBytes": 1048576,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "store": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/twweb.log"),
            "maxBytes": 1048576,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "status": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/twweb.status.log"),
            "maxBytes": 1048576,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "requests": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/twweb.requests.log"),
            "maxBytes": 1048576,
            "backupCount": 5,
            "formatter": "verbose",
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
            "handlers": ["exception_log", "store", "sentry", "syslog"],
            "propagate": True,
            "level": "INFO",
        },
        "django": {"handlers": ["null"], "propagate": True, "level": "INFO",},
        "gunicorn": {"handlers": ["null"], "level": "INFO", "propagate": True,},
        "requests": {"handlers": ["requests"], "level": "DEBUG", "propagate": True,},
        "selenium": {"handlers": ["null"], "level": "INFO", "propagate": True,},
        "inthe_am.taskmanager.taskwarrior_client": {
            "handlers": ["taskwarrior"],
            "level": "DEBUG",
            "propagate": True,
        },
        "inthe_am.taskmanager.tasks": {
            "handlers": ["tasks", "sentry"],
            "level": "DEBUG",
            "propagate": True,
        },
        "inthe_am.taskmanager.taskwarrior_client.export": {
            "handlers": ["taskwarrior", "sentry"],
            "level": "INFO",
            "propagate": False,
        },
        "inthe_am.taskmanager.taskwarrior_client.sync": {
            "handlers": ["taskwarrior", "sentry"],
            "level": "INFO",
            "propagate": False,
        },
        "inthe_am.taskmanager.management.commands": {
            "handlers": ["mgmt", "sentry"],
            "level": "INFO",
            "propagate": False,
        },
        "inthe_am.wsgi_status": {
            "handlers": ["status", "sentry"],
            "level": "INFO",
            "propagate": False,
        },
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
    "gunicorn",
    "inthe_am.taskmanager",
    "django_mailbox",
    "rest_framework",
    "rest_framework.authtoken",
    "django_extensions",
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
    INSTALLED_APPS.append("raven.contrib.django.raven_compat",)

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
