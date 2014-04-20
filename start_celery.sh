#!/bin/bash
set -e
source /var/www/envs/twweb/bin/activate
exec /var/www/envs/twweb/bin/celery -A inthe_am.taskmanager.celery worker -l info
