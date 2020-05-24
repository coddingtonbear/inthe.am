FROM alpine:3.11

ENV TASK_VERSION=2.5.1-r0

RUN apk update && \
  apk upgrade && \
  apk add --update --no-cache python3 postgresql-client git task=${TASK_VERSION} && \
  apk add --update --no-cache --virtual .build-deps gcc libc-dev linux-headers curl-dev \
          python3-dev postgresql-dev build-base gettext vim libxml2-dev libxslt-dev && \
pip3 install --upgrade pip
COPY requirements-frozen.txt /tmp
RUN pip3 install --no-cache -r /tmp/requirements-frozen.txt
# We need a version of uwsgi patched for musl since we're running on alpine
RUN pip3 uninstall -y uwsgi
RUN pip3 install https://github.com/unbit/uwsgi/archive/uwsgi-2.0.zip#egg=uwsgi
COPY external_python_modules/ /external_python_modules
RUN for mod in /external_python_modules/* ; do pip3 install -e $mod ; done
RUN apk del .build-deps

# TODO accept userid from build-arg
RUN addgroup -g 1000 -S django && \
    adduser -u 1000 -S django -G django
RUN apk add bash
USER django
VOLUME /data/web
WORKDIR /data/web
