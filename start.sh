#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
exec /var/www/envs/twweb/bin/python /var/www/twweb/manage.py run_gunicorn --config /var/www/twweb/gunicorn.conf.py
