#!/bin/bash
set -e
if [ ! -d /mnt/task_data/task_data]; then
    echo "Task data is not mounted!"
    exit 1
fi
source /var/www/envs/twweb/bin/activate
exec /var/www/envs/twweb/bin/uwsgi --ini /var/www/twweb/uwsgi.ini --stats /tmp/twweb.socket
