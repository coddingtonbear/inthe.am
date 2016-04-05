#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
export EVENTLET=true
export NEW_RELIC_CONFIG_FILE=/var/www/twweb/newrelic-status.ini
exec /var/www/envs/twweb/bin/newrelic-admin run-program /var/www/envs/twweb/bin/gunicorn inthe_am.wsgi --config /var/www/twweb/gunicorn_status.conf.py
