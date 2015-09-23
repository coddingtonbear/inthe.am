#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
export DJANGO_SETTINGS_MODULE=inthe_am.celery_settings
export NEW_RELIC_CONFIG_FILE=/var/www/twweb/newrelic-celery.ini
exec /var/www/envs/twweb/bin/newrelic-admin run-program /var/www/envs/twweb/bin/celery -A inthe_am.taskmanager.celery worker -l info
