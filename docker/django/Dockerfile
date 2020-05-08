FROM alpine:3.11

RUN apk update && \
  apk upgrade && \
  apk add --update --no-cache python3 postgresql-client git && \
  apk add --update --no-cache --virtual .build-deps  linux-headers curl-dev \
          python3-dev postgresql-dev build-base gettext vim libxml2-dev libxslt-dev && \
pip3 install --upgrade pip
COPY requirements-frozen.txt /tmp
RUN pip3 install --no-cache -r /tmp/requirements-frozen.txt && \
  apk del .build-deps
COPY external_python_modules/ /external_python_modules
RUN for mod in /external_python_modules/* ; do pip3 install -e $mod ; done

# TODO accept userid from build-arg
RUN addgroup -g 1000 -S django && \
    adduser -u 1000 -S django -G django
RUN apk add bash
USER django
VOLUME /data/web
WORKDIR /data/web
