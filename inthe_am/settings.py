"""
Django settings for inthe.am project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nou@d*dme8l60^9mzyk@#ikeobd0ws#p*mj#e*i*g33d#blsc9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
if os.uname()[1] == "norman":
    DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


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

ROOT_URLCONF = 'inthe_am.urls'

WSGI_APPLICATION = 'inthe_am.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

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
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
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
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/twweb.error.log'),
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
        }
    },
    'loggers': {
        '': {
            'handlers': ['exception_log', 'store'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'gunicorn': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211'
        }
    }

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"

SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTOCOL', 'https')

TASTYPIE_DATETIME_FORMATTING = 'rfc-2822'

SOCIAL_AUTH_SESSION_EXPIRATION = False

# Sourced from environment:
#  SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
#  SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
#  TASKD_BINARY
#  TASKD_SERVER
#  TASKD_ORG
#  TASKD_DATA
#  TASKD_SIGNING_TEMPLATE
#  TASK_BINARY
this_module = sys.modules[__name__]
for key, value in os.environ.items():
    if key.startswith(ENVIRONMENT_SETTING_PREFIX):
        setattr(
            this_module,
            key[len(ENVIRONMENT_SETTING_PREFIX):],
            value
        )
