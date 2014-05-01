#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
exec /var/www/envs/twweb/bin/python /var/www/twweb/manage.py run_gunicorn -k eventlet --config /var/www/twweb/gunicorn_status.conf.py
