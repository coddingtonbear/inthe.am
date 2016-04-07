#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
exec /var/www/envs/twweb/bin/uwsgi --gevent 50 --gevent-monkey-patch --ini /var/www/twweb/uwsgi_status.ini
