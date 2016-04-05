#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
exec /var/www/envs/twweb/bin/gunicorn inthe_am.wsgi_status --config /var/www/twweb/gunicorn_status.conf.py
