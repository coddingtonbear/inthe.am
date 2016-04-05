#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
exec /var/www/envs/twweb/bin/newrelic-admin run-program /var/www/envs/twweb/bin/gunicorn inthe_am.wsgi --config /var/www/twweb/gunicorn.conf.py
