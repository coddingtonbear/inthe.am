#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
exec /var/www/envs/twweb/bin/newrelic-admin run-program /var/www/envs/twweb/bin/uwsgi --ini /var/www/twweb/uwsgi.ini
