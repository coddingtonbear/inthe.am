#!/bin/bash
python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput

if [[ "${DJANGO_DEBUG}" == "1" ]]; then
    echo "Starting debug server..."
    python manage.py runserver 0.0.0.0:8000
else
    echo "Starting uwsgi server..."
    uwsgi --ini uwsgi.ini
fi
