#!/usr/bin/env bash
source /data/web/.env
source /data/web/.private.env

/usr/local/bin/python /data/web/manage.py "$@"
