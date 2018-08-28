#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
exec /var/www/envs/twweb/bin/uwsgi --ini /var/www/twweb/uwsgi.ini --stats /tmp/twweb.socket
