FROM python:3.8-slim

ENV TASK_VERSION=2.5.1-r0 DJANGO_SETTINGS_MODULE=inthe_am.settings

EXPOSE 8000

RUN apt-get update
RUN apt-get install -y postgresql-client git taskwarrior \
  python-dev gettext vim libxml2-dev libxslt-dev \
  libcurl4-gnutls-dev build-essential libgnutls28-dev \
  libpcre3 libpcre3-dev gnutls-bin supervisor cron \
  libpq-dev

RUN pip install --upgrade pip
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
COPY ./docker/django/gitconfig /root/.gitconfig

ARG CRONTAB=./docker/django/empty.crontab
COPY ${CRONTAB} /etc/cron/tasks.crontab
RUN chmod 0644 /etc/cron/tasks.crontab &&\
  crontab /etc/cron/tasks.crontab

ARG SUPERVISORD_CONFIG
COPY $SUPERVISORD_CONFIG /etc/supervisor/conf.d/service.conf

RUN chmod 777 /tmp/

VOLUME /data/web
WORKDIR /data/web

RUN mkdir /django-static
VOLUME /django-static

RUN mkdir /task_data
VOLUME /task_data

VOLUME /var/taskd

CMD /usr/bin/supervisord --nodaemon
