#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
export EVENTLET=true
export NEW_RELIC_CONFIG_FILE=/var/www/twweb/newrelic-status.ini
exec /var/www/envs/bin/newrelic-admin run-program /var/www/envs/twweb/bin/python /var/www/twweb/manage.py run_gunicorn -k eventlet --config /var/www/twweb/gunicorn_status.conf.py
