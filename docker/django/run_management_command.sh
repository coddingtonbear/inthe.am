#!/usr/bin/env bash
set -o allexport
source /data/web/.env
source /data/web/.private.env
set +o allexport

/usr/local/bin/python /data/web/manage.py "$@"
