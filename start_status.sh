#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
exec /var/www/envs/twweb/bin/uwsgi --ini /var/www/twweb/uwsgi_status.ini
