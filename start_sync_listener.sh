#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
exec /var/www/envs/twweb/bin/python /var/www/twweb/manage.py sync_listener
