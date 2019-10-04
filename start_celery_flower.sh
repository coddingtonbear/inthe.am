#!/bin/bash
set -e
if [ ! -d /mnt/task_data/task_data ]; then
    echo "Task data is not mounted!"
    exit 1
fi
cd /var/www/twweb
source /var/www/envs/twweb/bin/activate
export DJANGO_SETTINGS_MODULE=inthe_am.celery_settings
exec /var/www/envs/twweb/bin/celery flower -A inthe_am.taskmanager.celery worker --port=5555
