#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
exec /var/www/envs/twweb/bin/uwsgi --gevent 25 --ini /var/www/twweb/uwsgi_status.ini --status /tmp/twweb_status.socket
