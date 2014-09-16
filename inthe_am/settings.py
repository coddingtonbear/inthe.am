"""
Django settings for inthe.am project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from subprocess32 import check_output
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TRAVIS = True if os.environ.get('TRAVIS') else False
TESTING = ('test' in sys.argv) or TRAVIS

ADMINS = (
    ('Adam Coddington', 'admin@inthe.am'),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nou@d*dme8l60^9mzyk@#ikeobd0ws#p*mj#e*i*g33d#blsc9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
if os.uname()[1] == "eugene.adamcoddington.net":
    DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [
    'inthe.am',
]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social.apps.django_app.default',
    'gunicorn',
    'inthe_am.taskmanager',
    'django_mailbox',
    'south',
    'tastypie',
    'django_extensions',
    'raven.contrib.django.raven_compat',
    'django_behave',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {'access_type': 'offline'}

ROOT_URLCONF = 'inthe_am.urls'

WSGI_APPLICATION = 'inthe_am.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

CONN_MAX_AGE = None

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

ENVIRONMENT_SETTING_PREFIX = 'TWWEB_'

LOGIN_REDIRECT_URL = '/'

TASK_STORAGE_PATH = os.path.join(BASE_DIR, 'task_data')

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': (
                '%(levelname)s:%(name)s:%(asctime)s %(module)s %(process)d '
                '%(thread)d %(message)s'
            )
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'exception_log': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/twweb.error.log'),
            'maxBytes': 1048576,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'taskwarrior': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/twweb.taskwarrior.log'),
            'maxBytes': 1048576,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'store': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/twweb.log'),
            'maxBytes': 1048576,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.handlers.SentryHandler'
        }
    },
    'loggers': {
        '': {
            'handlers': ['exception_log', 'store', 'sentry'],
            'propagate': True,
            'level': 'INFO',
        },
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'gunicorn': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': True,
        },
        'selenium': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': True,
        },
        'inthe_am.taskmanager.taskwarrior_client': {
            'handlers': ['taskwarrior'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'inthe_am.taskmanager.taskwarrior_client.export': {
            'handlers': ['taskwarrior', 'sentry'],
            'level': 'INFO',
            'propagate': False,
        },
        'inthe_am.taskmanager.taskwarrior_client.sync': {
            'handlers': ['taskwarrior', 'sentry'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211'
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

TASTYPIE_DATETIME_FORMATTING = 'rfc-2822'

SOCIAL_AUTH_SESSION_EXPIRATION = False

TOS_VERSION = 1

RAVEN_DSN = ''
DATABASE_ENGINE = 'django.db.backends.sqlite3'
DATABASE_NAME = os.path.join(BASE_DIR, 'db.sqlite3')
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

EVENT_STREAM_TIMEOUT = 240
EVENT_STREAM_LOOP_INTERVAL = 5
EVENT_STREAM_POLLING_INTERVAL = 60
LOCKFILE_TIMEOUT_SECONDS = 120

TEST_RUNNER = 'django_behave.runner.DjangoBehaveTestSuiteRunner'

BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

TASKWARRIOR_CONFIG_OVERRIDES = {
    'uda': {
        'intheamattachments': {
            'type': 'string',
            'label': 'Inthe.AM Attachments',
        },
        'intheamoriginalemailsubject': {
            'type': 'string',
            'label': 'Inthe.AM E-mail Subject',
        },
        'intheamoriginalemailid': {
            'type': 'numeric',
            'label': 'Inthe.AM E-mail ID',
        }
    }
}

VERSION = check_output(
    [
        'git',
        '--work-tree=%s' % BASE_DIR,
        '--git-dir=%s' % os.path.join(BASE_DIR, '.git'),
        'rev-parse',
        'HEAD'
    ]
).strip()

if TESTING:
    CELERY_ALWAYS_EAGER = True

TASKD_BINARY = '/usr/local/bin/taskd'
TASK_BINARY = '/usr/local/bin/task'
TASKD_DATA = '/var/taskd'
TASKD_SIGNING_TEMPLATE = '/var/taskd/cert.template'
TASKD_SERVER = '127.0.0.1:53589'
TASKD_ORG = 'testing'

# Must be sourced from environment:
#  SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
#  SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
this_module = sys.modules[__name__]
for key, value in os.environ.items():
    if key.startswith(ENVIRONMENT_SETTING_PREFIX):
        setattr(
            this_module,
            key[len(ENVIRONMENT_SETTING_PREFIX):],
            value
        )


RAVEN_CONFIG = {
    'dsn': RAVEN_DSN
}

DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT
    }
}
