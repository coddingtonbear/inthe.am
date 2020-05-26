FROM python:3.8-slim

ENV TASK_VERSION=2.5.1-r0 DJANGO_SETTINGS_MODULE=inthe_am.settings

RUN apt-get update && \
  apt-get upgrade
RUN apt-get install -y postgresql-client git taskwarrior \
    python-dev gettext vim libxml2-dev libxslt-dev \
    libcurl4-gnutls-dev build-essential libgnutls28-dev \
    libpcre3 libpcre3-dev gnutls-bin

RUN pip install --upgrade pip
COPY requirements-frozen.txt /tmp
RUN pip install --no-cache -r /tmp/requirements-frozen.txt
COPY external_python_modules/ /external_python_modules
RUN for mod in /external_python_modules/* ; do pip install -e $mod ; done
COPY docker/django/gitconfig /var/www/.gitconfig

RUN chmod 777 /tmp/

VOLUME /data/web
WORKDIR /data/web

RUN mkdir /django-static
RUN chown www-data:www-data /django-static
VOLUME /django-static

RUN mkdir /task_data
RUN chown www-data:www-data /task_data
VOLUME /task_data

VOLUME /var/taskd

USER www-data
